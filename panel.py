from typing import Text
import bpy, os
# from  . easymocap_blender import VERSION
import json


def select_cam_updt(self, context):
    easymocap_properties = context.scene.easymocap_prop
    slct_cam = easymocap_properties.easymocap_cameras_list
    all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)
    all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)
    all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)

    path_prj = easymocap_properties.easymocap_prj_path
    path_prj_extri = os.path.join(path_prj, 'extri')

    for i in range(len(all_cam_data)):
        if int(all_cam_data[i][0]) == int(slct_cam):
            easymocap_properties.easymocap_camera_intri_video_path = all_cam_data[i][1]
            easymocap_properties.easymocap_camera_intri_description = all_cam_data[i][2]

    for i in range(len(all_cam_extri_data)):
        if int(all_cam_extri_data[i][0]) == int(slct_cam):
            easymocap_properties.easymocap_camera_extri_and_pose_video_path = all_cam_extri_data[i][1]

    for i in range(len(all_cam_extri_data)):
        if int(all_cam_extri_data[i][0]) == int(slct_cam):
            easymocap_properties.easymocap_camera_finalize_and_pose_video_path = all_cam_finalize_data[i][1]

    # updating the path of fix json, based on the selected camera, considering that the json fix will be save at the same folder as the image
    path_original_json = os.path.join(path_prj_extri, 'chessboard', '{:02d}'.format(int(slct_cam) + 1), '000000.json')
    path_fixed_json = os.path.join(path_prj_extri, 'images', '{:02d}'.format(int(slct_cam) + 1), '000000.json')
    easymocap_properties.easymocap_fix_json_original = path_original_json
    easymocap_properties.easymocap_fix_json_correct_data = path_fixed_json


def calib_list_updt(self, context):
    easymocap_properties = context.scene.easymocap_prop

    selected_calib_prj = easymocap_properties.easymocap_intri_calib_list
    if selected_calib_prj != 'select':
        qty_cam = int(selected_calib_prj.split('CAM_')[0])

        easymocap_properties.easymocap_qty_cameras = qty_cam

        # create empty camera list
        cam_paths = []
        for c in range(qty_cam):
            cam_paths.append([c, '', ''])

        easymocap_properties.easymocap_allcam_json_path = json.dumps(cam_paths)
        easymocap_properties.easymocap_allcam_extri_json_path = json.dumps(cam_paths)
        easymocap_properties.easymocap_allcam_finalize_json_path = json.dumps(cam_paths)

    # slct_cam = easymocap_properties.easymocap_cameras_list


def intri_configs_callback(scene, context):
    path_addon = os.path.dirname(os.path.abspath(__file__))
    path_intri = os.path.join(path_addon, '0_calib_intri')
    dirfile = os.listdir(path_intri)

    # name = context.scene.khaos_tool.sk_frac_name_collection
    # name_ctr = name+'-'
    items = []
    # colls = bpy.data.collections
    # frac_collection = context.scene.khaos_tool.sk_frac_collection
    # i=0

    ####
    # generate the custom size to search for Constraint name (to be able to use "startswith")
    # len_name_start_ctr = len(name+'-{:03}'.format(0))

    for i, d in enumerate(dirfile):
        if i == 0:
            items.append(("select", "Select an option", "Intrinsic Calib: Select one option"))
        # items.append((str(i),"%s" % d,"Intrinsic Calib: %s" % d))
        items.append((d, "%s" % d, "Intrinsic Calib: %s" % d))
        # print('my_settings_callback-coll_name: ',colls[x].name,' id: ',i)
    if len(items) == 0:
        # items.append((str(0),"Nothing","Intri Calib Available"))
        items.append(("nothing", "Nothing", "Intri Calib Available"))
    return items


def cameras_callback(scene, context):
    easymocap_properties = context.scene.easymocap_prop
    qty_cameras = easymocap_properties.easymocap_qty_cameras

    items = []
    for i in range(qty_cameras):
        # items.append((str(i),"%s" % colls[x].name,"Collection: %s" % colls[x].name))
        items.append((str(i), "%s" % "Camera " + str(i + 1), "Camera: %s" % str(i + 1)))
        # print('my_settings_callback-coll_name: ',colls[x].name,' id: ',i)
    return items


class AM_PT_Panel(bpy.types.Panel):
    bl_idname = "CEB_PT_Easymocap"
    bl_label = "Easymocap "  # +VERSION
    bl_category = "CEB"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        easymocap_properties = context.scene.easymocap_prop
        em_bool_set_cam = easymocap_properties.easymocap_bool_set_cam

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_master_profile = os.path.join(path_addon,
                                           '0_calib_intri')  # pasta com as calibragens (selecionar pasta final a partir do easymocap_intri_calib_list)
        path_intri_calib_selected = os.path.join(path_master_profile, easymocap_properties.easymocap_intri_calib_list)

        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_extri = os.path.join(path_prj, 'extri')
        path_prj_extri_out = os.path.join(path_prj_extri, 'output')  # pasta extri/output

        # pasta de calibragen selecionada, caminho para os arquivos
        intri_calib_slctd = os.path.join(path_intri_calib_selected, 'intri.yml')
        extri_calib_slctd = os.path.join(path_intri_calib_selected, 'extri.yml')

        # pasta de extri output, caminho para os arquivos
        intri_extri_out = os.path.join(path_prj_extri_out, 'intri.yml')
        extri_extri_out = os.path.join(path_prj_extri_out, 'extri.yml')

        path_prj_ouput = os.path.join(path_prj, 'output')

        # path_addon = os.path.dirname(os.path.abspath(__file__))
        # path_intri = os.path.join(path_addon,'0_calib_intri')

        # dirfile = os.listdir(path_intri)

        # full_path = os.path.join(path_addon,dirfile)
        # os.path.isdir(full_path)

        # Tentar montar essa parte mais pro futuro.
        """
        rowb = layout.row().box()
        rowb.label(text='Action Library')
        rowb.operator('animtools.browse_folder', text="Browse Action Library")

        rowb = layout.row().box()
        rowb.operator('animtools.add_action_to_lib', text="Save Action")

"""

        rowb = layout.row().box()
        row = rowb.row()
        # row.enabled = enable_ctr
        row.enabled = True
        row.prop(scene, "ceb_easymocap_exp_prj",
                 icon="TRIA_DOWN" if scene.ceb_easymocap_exp_prj else "TRIA_RIGHT",
                 icon_only=True, emboss=False
                 )
        row.label(text='New Project: ')

        if scene.ceb_easymocap_exp_prj:
            row = rowb.column()

            # row = layout.row().box()
            # row.label(text='Intri Calib')
            # row = layout.row()
            row.label(text='New Project')
            row.prop(easymocap_properties, "easymocap_qty_cameras")
            row.prop(easymocap_properties, 'easymocap_cam_resolution')
            row.prop(easymocap_properties, 'easymocap_cam_fps')
            row.prop(easymocap_properties, "easymocap_new_intri_setup", text='')

            # row.active = em_bool_set_cam
            # col = row.row(align = True)

            # row.operator('easymocap.set_cam', text="Set Cam")
            # row = layout.row()
            # row.operator('easymocap.clear_cam', text="Clear Cam")
            # row = layout.row()
            row.active = True
            row.operator('easymocap.new_intri_setup', text="New Setup")

        rowb = layout.row().box()
        row = rowb.row()
        # row.enabled = enable_ctr
        row.enabled = True
        row.prop(scene, "ceb_easymocap_exp0",
                 icon="TRIA_DOWN" if scene.ceb_easymocap_exp0 else "TRIA_RIGHT",
                 icon_only=True, emboss=False
                 )
        row.label(text='Project Data: ')

        if scene.ceb_easymocap_exp0:
            row = rowb.column()

            # row = layout.row().box()
            # row.label(text='Intri Calib')
            # row = layout.row()
            # row.label(text='New Project')
            # row.prop(easymocap_properties, "easymocap_new_intri_setup",text='')

            # # row = layout.row()
            # row.active=True
            # row.operator('easymocap.new_intri_setup', text="New Intri Setup")
            # row.separator()
            row.label(text='Project List')
            row.prop(easymocap_properties, "easymocap_intri_calib_list", text='')
            row.separator()
            row.label(text='Project Folder')
            row.prop(easymocap_properties, "easymocap_prj_path", text='')
            row.operator('easymocap.prj_path', text="Save Path")

            row.separator()
            # row = layout.row()
            # row = layout.row()

        row = layout.row().box()
        row.label(text='UI Selection')
        row.prop(easymocap_properties, "easymocap_ui", text='')

        col = row.row(align=True)
        col.operator('easymocap.last_ui', text='Last')
        col.operator('easymocap.next_ui', text='Next')

        if int(easymocap_properties.easymocap_ui) == 0:

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Intrinsic Calibration')
            # row = layout.row()
            # row.label(text='----------------------------------------')

            row = layout.row().box()
            row.label(text='01 - Intrinsic Calibration')
            row.prop(easymocap_properties, "easymocap_cameras_list")
            # row = layout.row()
            col2 = row.row(align=True)
            col3 = col2.row()
            if easymocap_properties.easymocap_cameras_list == '0':
                col3.active = False
                col3.operator('easymocap.no_action_buttom', text='Prev Cam')
            else:
                col3.active = True
                col3.operator('easymocap.prev_cam', text='Prev Cam')

            col4 = col2.row()
            if easymocap_properties.easymocap_cameras_list == str(easymocap_properties.easymocap_qty_cameras - 1):
                col4.active = False
                col4.operator('easymocap.no_action_buttom', text='Next Cam')
            else:
                col4.active = True
                col4.operator('easymocap.next_cam', text='Next Cam')
            # row = layout.row()

            col = row.row(align=True)
            # col.prop(easymocap_properties,"easymocap_camera_intri_video_path")
            col.operator('easymocap.select_intri_cam_path', text="Set")
            # row = layout.row().box()
            # col2 = row.column(align=True)
            # col2.prop(easymocap_properties,"easymocap_camera_intri_description")
            # col2.operator('easymocap.save_intri_video_path', text="Save Data")

            rowlist = row.column(align=True)
            if easymocap_properties.easymocap_allcam_json_path != '':
                all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)
                for c in all_cam_data:
                    if c[1] == '':
                        status = 'Empty'
                    else:
                        filename = os.path.basename(c[1])
                        status = filename + ' - ' + c[2]
                    rowlist.label(text='Cam: ' + str(int(c[0] + 1)) + ' - ' + status)
            # row = layout.row()
            row.operator('easymocap.save_intri_videos_on_project_path', text="Save Video")
            # row = layout.row()
            # row.separator()

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Frames Selection (for intri calib)')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            row = layout.row().box()
            row.label(text='02 - Frames Selection')
            row.label(text='To go to vse, first duplicate 3dview')
            # row = layout.row()
            col = row.row(align=True)
            col.operator('easymocap.change_view3d_to_vse', text="3d to VSE")
            col.operator('easymocap.change_vse_to_view3d', text="VSE to 3D")
            # row = layout.row()
            row.prop(easymocap_properties, "easymocap_cameras_list")
            # row = layout.row()
            row.operator('easymocap.load_on_vse', text="Load on VSE")
            # row = layout.row()

            row.operator('easymocap.render_selected_frames', text="Render Frames")

            # row = layout.row()
            # row = layout.row()
            # col2 = row.row(align = True)
            # col2.operator('easymocap.clear_markers', text="Clear Markers")
            # col2.operator('easymocap.clear_vse_strips', text="Clear VSE")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Intrinsic Pattern Detection')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            row = layout.row().box()
            row.label(text='03 - Intrinsic Pattern')
            col = row.row(align=False)
            col.prop(easymocap_properties, "easymocap_intri_pattern_grid", text='Pattern')
            col.prop(easymocap_properties, "easymocap_intri_grid_size", text='Size')

            # row = layout.row()
            # row = layout.row()
            row.operator('easymocap.detect_chessboard', text="Detect Chessboard")
            # row = layout.row()
            row.operator('easymocap.calibrate_intrinsic', text="Calibrate")
            # row = layout.row()
            row.operator('easymocap.save_intrinsic_profile', text="SAVE IN PROFILE")
            row.separator()
            row.separator()

            col = row.row(align=True)
            col.operator('easymocap.last_ui', text='Last')
            col.operator('easymocap.next_ui', text='Next')

        if int(easymocap_properties.easymocap_ui) == 1:
            # row = layout.row()
            # row.separator()
            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Extrinsic Video')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            row = layout.row().box()
            row.label(text='01 - Extrinsic Video')
            row.prop(easymocap_properties, "easymocap_cameras_list")
            # row = layout.row()
            col2 = row.row(align=True)
            col3 = col2.row()
            if easymocap_properties.easymocap_cameras_list == '0':
                col3.active = False
                col3.operator('easymocap.no_action_buttom', text='Prev Cam')
            else:
                col3.active = True
                col3.operator('easymocap.prev_cam', text='Prev Cam')

            col4 = col2.row()
            if easymocap_properties.easymocap_cameras_list == str(easymocap_properties.easymocap_qty_cameras - 1):
                col4.active = False
                col4.operator('easymocap.no_action_buttom', text='Next Cam')
            else:
                col4.active = True
                col4.operator('easymocap.next_cam', text='Next Cam')
            # row = layout.row()
            col = row.row(align=False)
            # col.prop(easymocap_properties,"easymocap_camera_extri_and_pose_video_path")
            col.operator('easymocap.extrinsic_and_pose_video_path', text="Set")

            # row = layout.row().box()
            # row.operator('easymocap.save_extri_video_path', text="Save Cam")
            rowlist = row.column(align=True)
            if easymocap_properties.easymocap_allcam_extri_json_path != '':
                all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)
                for c in all_cam_extri_data:
                    if c[1] == '':
                        status = 'Empty'
                    else:
                        filename = os.path.basename(c[1])
                        status = filename + ' - ' + c[2]
                    rowlist.label(text='Cam: ' + str(int(c[0] + 1)) + ' - ' + status)

            row.operator('easymocap.save_extri_videos_on_project_path', text="Save Video")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Frames Selection (Extrinsic calib)')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            row = layout.row().box()
            row.label(text='02 - Frames Selection')
            col = row.row(align=True)
            col.operator('easymocap.change_view3d_to_vse', text="3d to VSE")
            col.operator('easymocap.change_vse_to_view3d', text="VSE to 3D")
            # row = layout.row()
            row.prop(easymocap_properties, "easymocap_cameras_list", text='')
            # row = layout.row()
            row.operator('easymocap.load_extri_on_vse', text="Load on VSE")
            # row = layout.row()
            row.operator('easymocap.render_selected_extri_frames', text="Render Frames")
            # row = layout.row()
            # row = layout.row()
            col2 = row.row(align=True)
            col2.operator('easymocap.clear_markers', text="Clear Markers")
            # col2.operator('easymocap.clear_vse_strips', text="Clear VSE")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Extrinsic Pattern Detection')
            # row = layout.row()
            # row.label(text='Uses same Pattern and size from intrinsic')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            row = layout.row().box()
            row.label(text='03 - Extrinsic Pattern')
            row.operator('easymocap.detect_extri_chessboard', text="Detect Chessboard")
            # row = layout.row()
            # row.operator('easymocap.labelme', text="Manual Detect (labelme)")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Extrinsic Calibration and Check')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            ## Data para pegar os
            exists_intri_fold_extri_out = os.path.exists(intri_extri_out)
            exists_extri_fold_extri_out = os.path.exists(extri_extri_out)

            row = layout.row().box()
            row.label(text='04 - Extrinsic Calibration')
            # if not exists_intri_fold_extri_out or not exists_extri_fold_extri_out:
            #         row.operator('easymocap.copy_intri_extri_from_slect_prj_to_extri_out',text='Copy Calib data from Project')
            # else:
            row.operator('easymocap.calib_extri', text="Calibration")
            # row = layout.row()
            row.operator('easymocap.check_calib_extri_cross', text="Check Cross")
            # row = layout.row()
            row.operator('easymocap.check_calib_extri_cube', text="Check Cube")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Fix Json using corrected one in LabelMe')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            # rowb = layout.row().box()
            row = layout.row()
            # row.enabled = enable_ctr
            row.enabled = True
            row.prop(scene, "ceb_easymocap_exp_fix_json",
                     icon="TRIA_DOWN" if scene.ceb_easymocap_exp_fix_json else "TRIA_RIGHT",
                     icon_only=True, emboss=False
                     )
            row.label(text='04.1 - Fix Json: ')

            if scene.ceb_easymocap_exp_fix_json:
                # row = rowb.column()

                # row = layout.row().box()
                # row.label(text='Intri Calib')
                # row = layout.row()

                row = layout.row().box()
                row.label(text='Fix Json using corrected one in LabelMe')
                row.prop(easymocap_properties, "easymocap_cameras_list")
                col = row.row(align=True)
                col.prop(easymocap_properties, "easymocap_fix_json_original", text='Original')
                col.operator('easymocap.fix_json_original_path', text="Set")
                # row = layout.row()
                col2 = row.row(align=True)
                col2.prop(easymocap_properties, "easymocap_fix_json_correct_data", text='Correct')
                col2.operator('easymocap.fix_json_correct_data_path', text="Set")
                # row = layout.row()
                row.operator('easymocap.json_fix', text="Fix Json")
                row.operator('easymocap.calib_extri', text="Calibration")

            row = layout.row().box()
            row.separator()
            row.separator()

            col = row.row(align=True)
            col.operator('easymocap.last_ui', text='Last')
            col.operator('easymocap.next_ui', text='Next')

        if int(easymocap_properties.easymocap_ui) == 2:

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Extract and OpenPose')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            row = layout.row().box()
            row.label(text='01 - Finalize Video')
            row.prop(easymocap_properties, "easymocap_cameras_list")
            col2 = row.row(align=True)
            col3 = col2.row()
            if easymocap_properties.easymocap_cameras_list == '0':
                col3.active = False
                col3.operator('easymocap.no_action_buttom', text='Prev Cam')
            else:
                col3.active = True
                col3.operator('easymocap.prev_cam', text='Prev Cam')

            col4 = col2.row()
            if easymocap_properties.easymocap_cameras_list == str(easymocap_properties.easymocap_qty_cameras - 1):
                col4.active = False
                col4.operator('easymocap.no_action_buttom', text='Next Cam')
            else:
                col4.active = True
                col4.operator('easymocap.next_cam', text='Next Cam')
            # row = layout.row()
            col = row.row(align=False)
            # col.prop(easymocap_properties,"easymocap_camera_finalize_and_pose_video_path")
            col.operator('easymocap.finalize_and_pose_video_path', text="Set")

            # row = layout.row().box()
            # row.operator('easymocap.save_finalize_video_path', text="Save Cam")
            rowlist = row.column(align=True)
            if easymocap_properties.easymocap_allcam_finalize_json_path != '':
                all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)
                for c in all_cam_finalize_data:
                    if c[1] == '':
                        status = 'Empty'
                    else:
                        filename = os.path.basename(c[1])
                        status = filename + ' - ' + c[2]
                    rowlist.label(text='Cam: ' + str(int(c[0] + 1)) + ' - ' + status)

            row.operator('easymocap.save_finalize_videos_on_project_path', text="!!SAVE VIDEO!!")
            row.separator()
            row.separator()

            col2 = row.row(align=True)
            col2.operator('easymocap.change_view3d_to_vse', text="3d to VSE")
            col2.operator('easymocap.change_vse_to_view3d', text="VSE to 3D")
            # row = layout.row()
            # row.prop(easymocap_properties,"easymocap_cameras_list",text='')
            # row = layout.row()
            row.operator('easymocap.load_finalize_on_vse', text="Load on VSE")

            row = layout.row().box()
            row.label(text='02 - Extract and OpenPose')
            row.prop(easymocap_properties, "easymocap_openpose_path", text='')
            # row = layout.row()
            row.operator('easymocap.openpose_path', text="Set Path")
            # row = layout.row()
            row.prop(easymocap_properties, "easymocap_bool_openpose_render")
            # row = layout.row()
            row.prop(easymocap_properties, "easymocap_bool_openpose_hand_face")
            # row = layout.row()
            # row = layout.row()
            row.operator('easymocap.video_extract_and_openpose_pass', text="Extract/Run OpenPose")

            rowb = layout.row().box()
            row = rowb.row()
            # row.enabled = enable_ctr
            row.enabled = True
            row.prop(scene, "ceb_easymocap_exp_openpose_clear",
                     icon="TRIA_DOWN" if scene.ceb_easymocap_exp_openpose_clear else "TRIA_RIGHT",
                     icon_only=True, emboss=False
                     )
            row.label(text='OpenPose Clear: ')

            if scene.ceb_easymocap_exp_openpose_clear:
                row = rowb.column()
                row.prop(easymocap_properties, "easymocap_openpose_clear")
                row.operator('easymocap.clear_extract_and_openpose', text='Clear Selection')

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Import SMPL Model')
            # row = layout.row()
            # row.label(text='----------------------------------------')

            path_addon = os.path.dirname(os.path.abspath(__file__))
            path_smpl = os.path.join(path_addon, 'data', 'smplx', 'smpl')
            path_smplx = os.path.join(path_addon, 'data', 'smplx', 'smplx')
            smpl_model = easymocap_properties.easymocap_smpl_model_import
            smplx_model = easymocap_properties.easymocap_smplx_model_import

            smpl_model_path = os.path.join(path_smpl, smpl_model)
            smplx_model_path = os.path.join(path_smplx, smplx_model)

            row = layout.row().box()
            row.label(text='03.1 - Import SMPL Model')
            col = row.row(align=True)
            col.prop(easymocap_properties, "easymocap_smpl_model_import", text='')

            if not os.path.exists(smpl_model_path):
                col.operator('easymocap.import_smpl', text="Import")
            else:
                col.label(text='Model imported')

            row.label(text='03.2 - Import SMPLX Model')
            col2 = row.row(align=True)
            col2.prop(easymocap_properties, "easymocap_smplx_model_import", text='')
            if not os.path.exists(smplx_model_path):
                col2.operator('easymocap.import_smplx', text="Import")
            else:
                col2.label(text='Model imported')

            # row.operator('easymocap.remove_smpl_model', text="Remove Model")

            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()
            # row.label(text='Creating the Mocap')
            # row = layout.row()
            # row.label(text='----------------------------------------')
            # row = layout.row()

            row = layout.row().box()
            row.label(text='04 - Creating the Mocap')
            rowb = row.column(align=True)

            if easymocap_properties.easymocap_prj_path == '':
                rowb.label(text='SELECT THE PROJECT PATH')
                rowb.label(text='To view the TRIANGULATE Button')
                rowb.label(text='---------------------------------')
            else:
                rowb.operator('easymocap.triangulate', text="Triangulate")

            rowb.prop(easymocap_properties, "easymocap_bool_custom_cameras")
            if easymocap_properties.easymocap_bool_custom_cameras:
                rowb.label(text="    Add the cameras separating with ','")
                rowb.label(text="    Example: 1,3,5")
                rowb.prop(easymocap_properties, "easymocap_str_custom_cameras", text='')
                rowb.label(text=" ")

            # row.operator('easymocap.triangulate_simple', text="Triangulate Simple")
            rowb.prop(easymocap_properties, "easymocap_bool_start_end_option")
            if easymocap_properties.easymocap_bool_start_end_option:
                col = rowb.row(align=False)
                col.prop(easymocap_properties, 'easymocap_triang_start_frame')
                col.prop(easymocap_properties, 'easymocap_triang_end_frame')
            rowb.label(text='Options to create images')
            rowb.label(text='Useful for debugging')
            rowb.prop(easymocap_properties, "easymocap_bool_vis_det", text='Render Raw point data')
            rowb.prop(easymocap_properties, "easymocap_bool_vis_repro", text='Render Triangulates point data')
            rowb.prop(easymocap_properties, "easymocap_bool_write_full_smpl", text='Process Head and Fingers')

            # rowb.prop(easymocap_properties,"easymocap_bool_vis_smpl")
            rowb.separator()
            rowb.separator()
            rowb.separator()
            rowb.separator()
            rowb.separator()
            rowb.operator('easymocap.clear_triang_output', text="CLEAR TRIANGULATION OUTPUT")

            row.separator()
            row.separator()

            col = row.row(align=True)
            col.operator('easymocap.last_ui', text='Last')
            col.operator('easymocap.next_ui', text='Next')


from bpy.props import (StringProperty,
                       BoolProperty,
                       FloatProperty,
                       IntProperty,
                       EnumProperty
                       )
from bpy.types import (PropertyGroup)


class MySettings(PropertyGroup):
    easymocap_ui: EnumProperty(
        name="UI Steps:",
        description="List Steps to be done in the UI.",
        items=[
            ('0', 'Intrinsic', 'Intrinsic UI'),
            ('1', 'Extrinsic', 'Extrinsic UI'),
            ('2', 'Finalize', 'Finalize UI')
        ]
    )
    easymocap_intri_calib_list: EnumProperty(
        name="Intrisic Calibration:",
        description="List of Intrinsic Calibration configs.",
        items=intri_configs_callback,
        update=calib_list_updt
    )
    easymocap_cameras_list: EnumProperty(
        name="Cameras:",
        description="List of Cameras.",
        items=cameras_callback,
        update=select_cam_updt
    )
    # intrinsic setup, folder and all
    easymocap_new_intri_setup: StringProperty(name="Name for new Intri Setup",
                                              description="Name to create the new intri setup")
    easymocap_cam_resolution: IntProperty(name="Camera Resolution", description="Camera resolution", default=1080,
                                          min=0)
    easymocap_cam_fps: IntProperty(name="Camera FPS", description="Camera FPS", default=30, min=0)
    easymocap_qty_cameras: IntProperty(name="Quantity of Cameras", description="Amout of cameras to calibrate",
                                       default=2, min=2)

    easymocap_camera_intri_video_path: StringProperty(name="Path for Intri Camera Video",
                                                      description="Path for Camera Video")
    easymocap_camera_intri_description: StringProperty(name="Description of the intri camera",
                                                       description="Description of the intri  camera")
    easymocap_allcam_json_path: StringProperty(name="Json dump with all cameras",
                                               description="Json Dump with all cameras")
    easymocap_prj_path: StringProperty(name="Project Path", description="Project Path")
    easymocap_bool_set_cam: BoolProperty(default=True, name="Active inactive Set Cam")
    easymocap_intri_pattern_grid: StringProperty(name="Pattern Grid", description="Pattern Grid", default='3,5')
    easymocap_intri_grid_size: FloatProperty(name="Grid size in m", description="Grid size in m", default=0.0465,
                                             precision=4)
    # openpose
    easymocap_openpose_path: StringProperty(name="OpenPose Path", description="Openpose Path")
    easymocap_bool_openpose_render: BoolProperty(default=False, name="Render Openpose Pass")
    easymocap_bool_openpose_hand_face: BoolProperty(default=False, name="Detect hand and Face")
    ## Openpose clear options
    easymocap_openpose_clear: EnumProperty(
        name="Option to Clear:", description="Clear files to reprocess.",
        items=[
            ('annot', 'Annotation', 'Clear Annotation only'),
            ('annot_openpose', 'Annot & OpenPose', 'Clear Annotation and Openpose Data'),
            ('annot_openpose_images', 'Annot, OpenP & Images', 'Clear Annotation, OpenPoser Data and Image Sequence'),
        ]
    )

    # extrinsic/video part
    easymocap_camera_extri_and_pose_video_path: StringProperty(name="Path for Extrinsic and pose Camera Video",
                                                               description="Path for Extrinsic and pose Camera Video")
    easymocap_allcam_extri_json_path: StringProperty(name="Json dump with all extri cameras",
                                                     description="Json Dump with all extri cameras")
    # extrinsic json fix
    easymocap_fix_json_original: StringProperty(name="Json with wrong data", description="Json with wrong data")
    easymocap_fix_json_correct_data: StringProperty(name="Json with corrected data",
                                                    description="Json with corrected data")
    # smpl import model
    easymocap_smpl_model_import: EnumProperty(
        name="Smpl Model:", description="SMPL Model to import.",
        items=[
            ('SMPL_NEUTRAL.pkl', 'NEUTRAL', 'Neutral Model'),
            # ('SMPL_MALE.pkl','MALE','Neutral Model'),
            # ('SMPL_FEMALE.pkl','FEMALE','Neutral Model')
        ]
    )
    easymocap_smplx_model_import: EnumProperty(
        name="SMPLX Model:", description="SMPLX Model to import.",
        items=[
            ('SMPLX_NEUTRAL.pkl', 'NEUTRAL', 'Neutral Model'),
            # ('SMPLX_MALE.pkl','MALE','Neutral Model'),
            # ('SMPLX_FEMALE.pkl','FEMALE','Neutral Model')
        ]
    )
    # options on the triangulate
    easymocap_camera_finalize_and_pose_video_path: StringProperty(name="Path for finalize and pose Camera Video",
                                                                  description="Path for finalize and pose Camera Video")
    easymocap_allcam_finalize_json_path: StringProperty(name="Json dump with all finalize cameras",
                                                        description="Json Dump with all finalize cameras")
    easymocap_bool_custom_cameras: BoolProperty(default=False, name="Custom Cameras")
    easymocap_str_custom_cameras: StringProperty(name="Custom Cameras")
    easymocap_bool_vis_det: BoolProperty(default=False, name="vis_det")
    easymocap_bool_vis_repro: BoolProperty(default=False, name="vis_repro")
    easymocap_bool_vis_smpl: BoolProperty(default=False, name="vis_smpl")
    easymocap_bool_write_full_smpl: BoolProperty(default=False, name="write_full_smpl")
    easymocap_bool_start_end_option: BoolProperty(default=False, name="Select Start and End frame")
    easymocap_triang_start_frame: IntProperty(name="Start Frame", description="Start Frame for Triangulation",
                                              default=0, min=0)
    easymocap_triang_end_frame: IntProperty(name="End Frame", description="Start Frame for Triangulation", default=200,
                                            min=0)

#     # Bool : BoolProperty(default=True, name="Check Box")
#     am_stride: FloatProperty(name="stride", description="size of stride", default=0.0)
