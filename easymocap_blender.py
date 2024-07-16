import os, subprocess, sys
from typing import Pattern
import bpy, glob
from bpy.types import Operator
# from . helper import Helper
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
import json
from shutil import copyfile, rmtree
from .apps.calibration import detect_chessboard, calib_intri, calib_extri, check_calib
from .scripts.preprocess import extract_video
from .apps.demo import mv1p
from os.path import join
# global VERSION
# VERSION = '0.11'

from contextlib import contextmanager


@contextmanager
def context(area_type: str):
    area = bpy.context.area
    former_area_type = area.type
    area.type = area_type
    try:
        yield area
    finally:
        area.type = former_area_type


class ExtractSelectedFramesIntri(Operator):
    bl_idname = "easymocap.extract_selected_frames_intri"
    bl_label = "Extract selected frames for Intrinsic Calibration"
    bl_description = "Extract selected frames for Intrinsic Calibration"

    def execute(self, context):
        return {'FINISHED'}


class NewIntriSetup(Operator):
    bl_idname = "easymocap.new_intri_setup"
    bl_label = "Create new Intri setup"
    bl_description = "Create new Intri setup"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        # comandos para criar pasta
        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_intri = os.path.join(path_addon, '0_calib_intri')
        dirfile = os.listdir(path_intri)

        qtd_cam = easymocap_properties.easymocap_qty_cameras
        cam_resolution = easymocap_properties.easymocap_cam_resolution
        cam_fps = easymocap_properties.easymocap_cam_fps
        new_intri_setup = easymocap_properties.easymocap_new_intri_setup

        new_folder = '{:02d}'.format(int(qtd_cam)) + "CAM_" + str(cam_resolution) + "_" + str(
            cam_fps) + "_fps_" + new_intri_setup
        new_folder_replace = new_folder.replace(' ', '_')

        path_new_intri_setup = os.path.join(path_intri, new_folder_replace)

        # checa se pasta existe e cria
        if not os.path.exists(path_new_intri_setup):
            os.makedirs(path_new_intri_setup)

        return {'FINISHED'}


class SetCameras(Operator):
    bl_idname = "easymocap.set_cam"
    bl_label = "Set Cameras"
    bl_description = "Fix the amount of cameras and create variables for it"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        easymocap_properties.easymocap_bool_set_cam = False
        qty_cam = easymocap_properties.easymocap_qty_cameras

        cam_paths = []
        for c in range(qty_cam):
            cam_paths.append([c, '', ''])

        easymocap_properties.easymocap_allcam_json_path = json.dumps(cam_paths)
        easymocap_properties.easymocap_allcam_extri_json_path = json.dumps(cam_paths)
        return {'FINISHED'}


class ClearCameras(Operator):
    bl_idname = "easymocap.clear_cam"
    bl_label = "Clear Cameras"
    bl_description = "Clear Cameras"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        easymocap_properties.easymocap_bool_set_cam = True

        easymocap_properties.easymocap_allcam_json_path = ''  # clean what is in memory

        return {'FINISHED'}


class SelectIntriCamPath(Operator, ImportHelper):
    bl_idname = "easymocap.select_intri_cam_path"
    bl_label = "Select path"
    bl_description = "Select path"

    # filename_ext = ".mp4"
    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        path = self.filepath
        easymocap_properties.easymocap_camera_intri_video_path = path

        ###Save data
        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)
        path = easymocap_properties.easymocap_camera_intri_video_path
        cam_desc = easymocap_properties.easymocap_camera_intri_description

        for i in range(len(all_cam_data)):
            if int(all_cam_data[i][0]) == int(slct_cam):
                all_cam_data[i][1] = path
                all_cam_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_json_path = json.dumps(all_cam_data)

        return {'FINISHED'}


class SaveIntriVideoPath(Operator):
    bl_idname = "easymocap.save_intri_video_path"
    bl_label = "Save path from the selected video"
    bl_description = "Save path from the selected video"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)
        path = easymocap_properties.easymocap_camera_intri_video_path
        cam_desc = easymocap_properties.easymocap_camera_intri_description

        for i in range(len(all_cam_data)):
            if int(all_cam_data[i][0]) == int(slct_cam):
                all_cam_data[i][1] = path
                all_cam_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_json_path = json.dumps(all_cam_data)

        return {'FINISHED'}


class LoadOnVSE(Operator):
    bl_idname = "easymocap.load_on_vse"
    bl_label = "load video on vse"
    bl_description = "load video on vse"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)
        path = easymocap_properties.easymocap_camera_intri_video_path
        cam_desc = easymocap_properties.easymocap_camera_intri_description

        # clear Markers
        context.scene.timeline_markers.clear()
        #### clear vse
        scene = context.scene
        seq = scene.sequence_editor
        # stips meta_strips
        for strip in seq.sequences:
            print(strip.name)
        # all strips
        for strip in seq.sequences_all:
            print(strip.name)
        # remove
        for strip in seq.sequences:
            seq.sequences.remove(strip)
        ### end clear vse

        for i in range(len(all_cam_data)):
            if int(all_cam_data[i][0]) == int(slct_cam):
                path_final = all_cam_data[i][1]

                bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=os.path.basename(path_final),
                    filepath=path_final,
                    channel=0,
                    frame_start=0)

        bpy.ops.sequencer.set_range_to_strips()  # scale frames to strip loaded

        bpy.context.scene.sequence_editor.active_strip = bpy.context.scene.sequence_editor.sequences[
            0]  # coloca o primeiro sequence como o ativo
        bpy.ops.sequencer.rendersize()  # seta a resolucao para render o mesmo que o video
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.render.fps = int(
            bpy.context.scene.sequence_editor.sequences[0].fps)  # render fps o mesmo que o do video carregado

        return {'FINISHED'}


class ExportIntriFrames(Operator):
    bl_idname = "easymocap.export_intri_frames"
    bl_label = "Export Intri Frames from markers"
    bl_description = "Export Intri Frames from Markers"

    def execute(self, context):
        markers = context.scene.timeline_markers
        for m in markers:
            print('frame: ' + m.frame)
            ##### falta terminar de programar, colocar para exportar frames que estão nos markers

        return {'FINISHED'}


class ClearMarkers(Operator):
    bl_idname = "easymocap.clear_markers"
    bl_label = "Clear Markers"
    bl_description = "Clear Markers"

    def execute(self, context):
        context.scene.timeline_markers.clear()
        return {'FINISHED'}


class ClearVSEStrips(Operator):
    bl_idname = "easymocap.clear_vse_strips"
    bl_label = "Clear VSE Strips"
    bl_description = "Clear VSE Strips"

    def execute(self, context):

        scene = context.scene
        seq = scene.sequence_editor
        # stips meta_strips
        for strip in seq.sequences:
            print(strip.name)
        # all strips
        for strip in seq.sequences_all:
            print(strip.name)
        # remove
        for strip in seq.sequences:
            seq.sequences.remove(strip)
        return {'FINISHED'}


class ChangeView3dToVSE(Operator):
    bl_idname = "easymocap.change_view3d_to_vse"
    bl_label = "change view3d to vse"
    bl_description = "change view3d to vse"

    def execute(self, context):
        # for area in bpy.context.screen.areas:
        #     if area.type == 'VIEW_3D':
        #         area.type = 'SEQUENCE_EDITOR'
        #         space_data = area.spaces.active
        #         break
        # else:
        #     space_data = None
        i = 0
        j = 0
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if i > 0:  # para nao mudar a primeira janela
                    area.type = 'SEQUENCE_EDITOR'
                    space_data = area.spaces.active
                    break
                i = i + 1
        else:
            space_data = None

        if space_data is not None:
            pass

        space_data.view_type = 'SEQUENCER_PREVIEW'
        return {'FINISHED'}


class ChangeVSEToView3d(Operator):
    bl_idname = "easymocap.change_vse_to_view3d"
    bl_label = "change vse to view3d"
    bl_description = "change vse to view3d"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'SEQUENCE_EDITOR':
                area.type = 'VIEW_3D'

        return {'FINISHED'}


class RenderSelectedFrames(Operator):
    bl_idname = "easymocap.render_selected_frames"
    bl_label = "Render selected frames"
    bl_description = "Render selected frames"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        scene = bpy.context.scene
        fp = scene.render.filepath  # get existing output path
        # scene.render.image_settings.file_format = 'PNG' # set output format to .png
        scene.render.image_settings.file_format = 'JPEG'  # set output format to .png

        frames = []

        for f in scene.timeline_markers:
            frames.append(f.frame)

        path_prj = easymocap_properties.easymocap_prj_path
        slct_cam = easymocap_properties.easymocap_cameras_list
        slct_cam_frmtd = '{:02d}'.format(int(slct_cam) + 1)

        path_prj_intri = os.path.join(path_prj, 'intrinsic')
        if not os.path.exists(path_prj_intri):
            os.makedirs(path_prj_intri)

        path_prj_intri_img = os.path.join(path_prj_intri, 'images')
        if not os.path.exists(path_prj_intri_img):
            os.makedirs(path_prj_intri_img)

        path_prj_intri_img_nmbr = os.path.join(path_prj_intri_img, slct_cam_frmtd)
        if not os.path.exists(path_prj_intri_img_nmbr):
            os.makedirs(path_prj_intri_img_nmbr)

        for frame_nr in frames:
            # set current frame to frame 5
            scene.frame_set(frame_nr)

            # set output path so render won't get overwritten
            # scene.render.filepath = os.path.join(path_prj_intri_img_nmbr , str(frame_nr))
            scene.render.filepath = os.path.join(path_prj_intri_img_nmbr, '{:06d}'.format(frame_nr))
            bpy.ops.render.render(write_still=True)  # render still

        # restore the filepath
        scene.render.filepath = fp

        return {'FINISHED'}


class PrjPath(Operator, ImportHelper):
    bl_idname = "easymocap.prj_path"
    bl_label = "Project path"
    bl_description = "Project path"

    # filename_ext = ".mp4"
    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_prj_path = os.path.dirname(self.filepath)

        return {'FINISHED'}


class SaveIntriVideosOnPrjPath(Operator):
    bl_idname = "easymocap.save_intri_videos_on_project_path"
    bl_label = "Save videos on prjct path"
    bl_description = "Save videos on prjct path"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        path_prj = easymocap_properties.easymocap_prj_path

        all_cam_data = json.loads(easymocap_properties.easymocap_allcam_json_path)

        path_prj_intri = os.path.join(path_prj, 'intrinsic')
        if not os.path.exists(path_prj_intri):
            os.makedirs(path_prj_intri)
        path_prj_intri_videos = os.path.join(path_prj_intri, 'videos')
        if not os.path.exists(path_prj_intri_videos):
            os.makedirs(path_prj_intri_videos)

        for vid in all_cam_data:
            src = vid[1]
            filename, extension = os.path.splitext(src)
            dst = os.path.join(path_prj_intri_videos, '{:02d}'.format(int(vid[0]) + 1) + extension)
            copyfile(src, dst)

        return {'FINISHED'}


class DetectChessboard(Operator):
    bl_idname = "easymocap.detect_chessboard"
    bl_label = "Detect Chessboard"
    bl_description = "Detect Chessboard"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_intri = os.path.join(path_prj, 'intrinsic')
        path_prj_out = os.path.join(path_prj_intri, 'output')

        x_pat = easymocap_properties.easymocap_intri_pattern_grid
        pattern_grid = []
        pattern_grid.append(int(x_pat.split(',')[0]))
        pattern_grid.append(int(x_pat.split(',')[1]))

        grid = easymocap_properties.easymocap_intri_grid_size
        ext = '.jpg'
        max_step = 50
        min_step = 0
        silent = False
        debug = False
        seq = False

        if seq:
            detect_chessboard.detect_chessboard_sequence(path_prj_intri, path_prj_out, pattern_grid, grid, ext, silent,
                                                         debug, min_step, max_step)
        else:
            detect_chessboard.detect_chessboard(path_prj_intri, path_prj_out, pattern_grid, grid, ext, silent, debug)

        # detect_chessboard.detect_chessboard(path_prj_intri, path_prj_out, pattern_grid,grid,ext,silent,debug)
        # detect_chessboard.detect_chessboard_sequence(path_prj_intri, path_prj_out, pattern_grid,grid,ext,silent,debug,min_step,max_step)

        return {'FINISHED'}


class CalibrateIntrinsic(Operator):
    bl_idname = "easymocap.calibrate_intrinsic"
    bl_label = "Calibrete Intrinsic"
    bl_description = "Calibrate Intrinsic"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_intri = os.path.join(path_prj, 'intrinsic')

        step = 1
        share_intri = False
        debug = False
        remove = False

        # calib_intri.calib_intri_share(path_prj_intri,step,remove)
        # calib_intri.calib_intri(path_prj_intri,step)

        if share_intri:
            calib_intri.calib_intri_share(path_prj_intri, step, remove)
        else:
            calib_intri.calib_intri(path_prj_intri, step)

        return {'FINISHED'}


class SaveIntrinsicProfile(Operator):
    bl_idname = "easymocap.save_intrinsic_profile"
    bl_label = "Save Intrinsic Profile"
    bl_description = "Save Intrinsic Profile"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_master_profile = os.path.join(path_addon, '0_calib_intri')
        current_profile = easymocap_properties.easymocap_intri_calib_list
        path_current_profile = os.path.join(path_master_profile, current_profile)
        intri_yml_profile = os.path.join(path_current_profile, 'intri.yml')

        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_intri = os.path.join(path_prj, 'intrinsic')
        path_prj_intri_out = os.path.join(path_prj_intri, 'output')
        intri_yml_intri = os.path.join(path_prj_intri_out, 'intri.yml')

        # copy intry to extri/output
        copyfile(intri_yml_intri, intri_yml_profile)

        return {'FINISHED'}


class OpenPosePath(Operator, ImportHelper):
    bl_idname = "easymocap.openpose_path"
    bl_label = "Openpose path"
    bl_description = "Openpose path"

    filename_ext = ".exe"
    filter_glob: StringProperty(
        default="*.exe",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_openpose_path = os.path.dirname(self.filepath)

        return {'FINISHED'}


class ExtrinsicAndPoseVideoPath(Operator, ImportHelper):
    bl_idname = "easymocap.extrinsic_and_pose_video_path"
    bl_label = "Path to Extrinsic and pose video path"
    bl_description = "Path to Extrinsic and pose video path"

    # filename_ext = ".mp4"
    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_camera_extri_and_pose_video_path = self.filepath

        ## save the data
        # easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)
        path = easymocap_properties.easymocap_camera_extri_and_pose_video_path

        for i in range(len(all_cam_extri_data)):
            if int(all_cam_extri_data[i][0]) == int(slct_cam):
                all_cam_extri_data[i][1] = path
                # all_cam_extri_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_extri_json_path = json.dumps(all_cam_extri_data)

        return {'FINISHED'}


class FinalizeAndPoseVideoPath(Operator, ImportHelper):
    bl_idname = "easymocap.finalize_and_pose_video_path"
    bl_label = "Path to Finalize and pose video path"
    bl_description = "Path to Finalize and pose video path"

    # filename_ext = ".mp4"
    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_camera_finalize_and_pose_video_path = self.filepath

        ###saving the data
        # easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)
        path = easymocap_properties.easymocap_camera_finalize_and_pose_video_path

        for i in range(len(all_cam_finalize_data)):
            if int(all_cam_finalize_data[i][0]) == int(slct_cam):
                all_cam_finalize_data[i][1] = path
                # all_cam_finalize_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_finalize_json_path = json.dumps(all_cam_finalize_data)

        return {'FINISHED'}


class SaveExtriVideoPath(Operator):
    bl_idname = "easymocap.save_extri_video_path"
    bl_label = "Save path from the extri selected video"
    bl_description = "Save path from the extri selected video"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)
        path = easymocap_properties.easymocap_camera_extri_and_pose_video_path

        for i in range(len(all_cam_extri_data)):
            if int(all_cam_extri_data[i][0]) == int(slct_cam):
                all_cam_extri_data[i][1] = path
                # all_cam_extri_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_extri_json_path = json.dumps(all_cam_extri_data)

        return {'FINISHED'}


class SaveFinalizeVideoPath(Operator):
    bl_idname = "easymocap.save_finalize_video_path"
    bl_label = "Save path from the finalize selected video"
    bl_description = "Save path from the finalize selected video"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)
        path = easymocap_properties.easymocap_camera_finalize_and_pose_video_path

        for i in range(len(all_cam_finalize_data)):
            if int(all_cam_finalize_data[i][0]) == int(slct_cam):
                all_cam_finalize_data[i][1] = path
                # all_cam_finalize_data[i][2] = cam_desc
        easymocap_properties.easymocap_allcam_finalize_json_path = json.dumps(all_cam_finalize_data)

        return {'FINISHED'}


class SaveExtriVideosOnPrjPath(Operator):
    bl_idname = "easymocap.save_extri_videos_on_project_path"
    bl_label = "Save extri videos on prjct path"
    bl_description = "Save extri videos on prjct path"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        path_prj = easymocap_properties.easymocap_prj_path

        all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)

        path_prj_videos = os.path.join(path_prj, 'extri', 'videos')
        if not os.path.exists(path_prj_videos):
            os.makedirs(path_prj_videos)

        for vid in all_cam_extri_data:
            src = vid[1]
            filename, extension = os.path.splitext(src)
            dst = os.path.join(path_prj_videos, '{:02d}'.format(int(vid[0]) + 1) + extension)
            copyfile(src, dst)

        return {'FINISHED'}


class SaveFinalizeVideosOnPrjPath(Operator):
    bl_idname = "easymocap.save_finalize_videos_on_project_path"
    bl_label = "Save extri videos on prjct path"
    bl_description = "Save extri videos on prjct path"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        path_prj = easymocap_properties.easymocap_prj_path

        all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)

        path_prj_videos = os.path.join(path_prj, 'videos')
        if not os.path.exists(path_prj_videos):
            os.makedirs(path_prj_videos)

        for vid in all_cam_finalize_data:
            src = vid[1]
            filename, extension = os.path.splitext(src)
            dst = os.path.join(path_prj_videos, '{:02d}'.format(int(vid[0]) + 1) + extension)
            copyfile(src, dst)

        return {'FINISHED'}


class LoadExtriOnVSE(Operator):
    bl_idname = "easymocap.load_extri_on_vse"
    bl_label = "load extrinsic video on vse"
    bl_description = "load extrinsic video on vse"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_extri_data = json.loads(easymocap_properties.easymocap_allcam_extri_json_path)

        # clear Markers
        # context.scene.timeline_markers.clear()
        #### clear vse
        scene = context.scene
        seq = scene.sequence_editor
        # stips meta_strips
        for strip in seq.sequences:
            print(strip.name)
        # all strips
        for strip in seq.sequences_all:
            print(strip.name)
        # remove
        for strip in seq.sequences:
            seq.sequences.remove(strip)
        ### end clear vse

        for i in range(len(all_cam_extri_data)):
            if int(all_cam_extri_data[i][0]) == int(slct_cam):
                path_final = all_cam_extri_data[i][1]

                bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=os.path.basename(path_final),
                    filepath=path_final,
                    channel=0,
                    frame_start=0)

        bpy.ops.sequencer.set_range_to_strips()  # scale frames to strip loaded

        bpy.context.scene.sequence_editor.active_strip = bpy.context.scene.sequence_editor.sequences[
            0]  # coloca o primeiro sequence como o ativo
        bpy.ops.sequencer.rendersize()  # seta a resolucao para render o mesmo que o video
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.render.fps = int(
            bpy.context.scene.sequence_editor.sequences[0].fps)  # render fps o mesmo que o do video carregado

        bpy.context.scene.frame_current = 0

        return {'FINISHED'}


class LoadFinalizeOnVSE(Operator):
    bl_idname = "easymocap.load_finalize_on_vse"
    bl_label = "load Finalize video on vse"
    bl_description = "load Finalize video on vse"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        all_cam_finalize_data = json.loads(easymocap_properties.easymocap_allcam_finalize_json_path)

        # clear Markers
        # context.scene.timeline_markers.clear()
        #### clear vse
        scene = context.scene
        seq = scene.sequence_editor
        # stips meta_strips
        for strip in seq.sequences:
            print(strip.name)
        # all strips
        for strip in seq.sequences_all:
            print(strip.name)
        # remove
        for strip in seq.sequences:
            seq.sequences.remove(strip)
        ### end clear vse

        for i in range(len(all_cam_finalize_data)):
            if int(all_cam_finalize_data[i][0]) == int(slct_cam):
                path_final = all_cam_finalize_data[i][1]

                bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=os.path.basename(path_final),
                    filepath=path_final,
                    channel=0,
                    frame_start=0)

        bpy.ops.sequencer.set_range_to_strips()  # scale frames to strip loaded

        bpy.context.scene.sequence_editor.active_strip = bpy.context.scene.sequence_editor.sequences[
            0]  # coloca o primeiro sequence como o ativo
        # bpy.ops.sequencer.rendersize() #seta a resolucao para render o mesmo que o video
        # bpy.context.scene.render.resolution_percentage = 100
        # bpy.context.scene.render.fps = int(bpy.context.scene.sequence_editor.sequences[0].fps) #render fps o mesmo que o do video carregado

        return {'FINISHED'}


class RenderSelectedExtriFrames(Operator):
    bl_idname = "easymocap.render_selected_extri_frames"
    bl_label = "Render selected Extri frames"
    bl_description = "Render selected Extri frames"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop

        scene = bpy.context.scene
        fp = scene.render.filepath  # get existing output path
        # scene.render.image_settings.file_format = 'PNG' # set output format to .png
        scene.render.image_settings.file_format = 'JPEG'  # set output format to .png

        frames = []

        for f in scene.timeline_markers:
            frames.append(f.frame)

        path_prj = easymocap_properties.easymocap_prj_path
        slct_cam = easymocap_properties.easymocap_cameras_list
        slct_cam_frmtd = '{:02d}'.format(int(slct_cam) + 1)

        path_prj_extri = os.path.join(path_prj, 'extri')
        if not os.path.exists(path_prj_extri):
            os.makedirs(path_prj_extri)

        path_prj_extri_img = os.path.join(path_prj_extri, 'images')
        if not os.path.exists(path_prj_extri_img):
            os.makedirs(path_prj_extri_img)

        path_prj_extri_img_nmbr = os.path.join(path_prj_extri_img, slct_cam_frmtd)
        if not os.path.exists(path_prj_extri_img_nmbr):
            os.makedirs(path_prj_extri_img_nmbr)

        for frame_nr in frames:
            # set current frame to frame 5
            scene.frame_set(frame_nr)

            # set output path so render won't get overwritten
            # scene.render.filepath = os.path.join(path_prj_intri_img_nmbr , str(frame_nr))
            # scene.render.filepath = os.path.join(path_prj_extri_img_nmbr , '{:06d}'.format(frame_nr))
            scene.render.filepath = os.path.join(path_prj_extri_img_nmbr, '{:06d}'.format(
                0))  # salvar como nome 000000, importante para parte do processo
            bpy.ops.render.render(write_still=True)  # render still

        # restore the filepath
        scene.render.filepath = fp

        return {'FINISHED'}


class DetectExtriChessboard(Operator):
    bl_idname = "easymocap.detect_extri_chessboard"
    bl_label = "Detect Extri Chessboard"
    bl_description = "Detect Extri Chessboard"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_extri = os.path.join(path_prj, 'extri')
        path_prj_out = os.path.join(path_prj_extri, 'output')

        x_pat = easymocap_properties.easymocap_intri_pattern_grid
        pattern_grid = []
        pattern_grid.append(int(x_pat.split(',')[0]))
        pattern_grid.append(int(x_pat.split(',')[1]))

        grid = easymocap_properties.easymocap_intri_grid_size
        ext = '.jpg'
        max_step = 50
        min_step = 0
        silent = False
        debug = False
        seq = False

        if seq:
            detect_chessboard.detect_chessboard_sequence(path_prj_extri, path_prj_out, pattern_grid, grid, ext, silent,
                                                         debug, min_step, max_step)
        else:
            detect_chessboard.detect_chessboard(path_prj_extri, path_prj_out, pattern_grid, grid, ext, silent, debug)

        # detect_chessboard.detect_chessboard(path_prj_intri, path_prj_out, pattern_grid,grid,ext,silent,debug)
        # detect_chessboard.detect_chessboard_sequence(path_prj_intri, path_prj_out, pattern_grid,grid,ext,silent,debug,min_step,max_step)

        return {'FINISHED'}


class LabelMe(Operator):
    bl_idname = "easymocap.labelme"
    bl_label = "Execute LabelMe"
    bl_description = "Execute Labelme"

    def execute(self, context):
        path = sys.executable
        labelme_exe = path.replace('bin\\python.EXE', 'Scripts\\labelme.exe')  # nao consegui fazer funcionar
        subprocess.check_call([labelme_exe])

        return {'FINISHED'}


class FixJsonOriginalPath(Operator, ImportHelper):
    bl_idname = "easymocap.fix_json_original_path"
    bl_label = "Openpose path"
    bl_description = "Openpose path"

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_fix_json_original = self.filepath

        return {'FINISHED'}


class FixJsonCorrectedDataPath(Operator, ImportHelper):
    bl_idname = "easymocap.fix_json_correct_data_path"
    bl_label = "Openpose path"
    bl_description = "Openpose path"

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        # path  = self.filepath
        easymocap_properties.easymocap_fix_json_correct_data = self.filepath

        return {'FINISHED'}


class JsonFix(Operator):
    bl_idname = "easymocap.json_fix"
    bl_label = "Fix json "
    bl_description = "Fix Json based on labeme annotation"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        path_old = easymocap_properties.easymocap_fix_json_original
        path_new = easymocap_properties.easymocap_fix_json_correct_data

        # path_old = r'C:\MOCAP\Blender_MOCAP\extri\chessboard\02\000001.json'
        # path_old_corrected = r'C:\MOCAP\Blender_MOCAP\extri\chessboard\02\000001_alterado.json'
        # path_new = r'C:\MOCAP\Blender_MOCAP\extri\images\02\000001.json'

        # carrega versao errada
        with open(path_old) as f:
            data = json.load(f)

        # carrega versao corrigida no labelme
        with open(path_new) as f:
            data_new = json.load(f)

        # novos dados
        new = data_new['shapes'][0]['points']

        for i in range(len(data['keypoints2d'])):
            data['keypoints2d'][i][0] = new[i][0]
            data['keypoints2d'][i][1] = new[i][1]
            data['keypoints2d'][i][2] = 1.0  # para colocar tudo como 1

        # salva
        with open(path_old, 'w') as f:
            json.dump(data, f, indent=4)

        return {'FINISHED'}


class CalibExtri(Operator):
    bl_idname = "easymocap.calib_extri"
    bl_label = "Calibrate Extrinsic"
    bl_description = "Calibrate Extrinsic"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_extri = os.path.join(path_prj, 'extri')
        path_prj_extri_output = os.path.join(path_prj_extri, 'output')
        if not os.path.exists(path_prj_extri_output):
            os.makedirs(path_prj_extri_output)

        # path_prj_intri = os.path.join(path_prj,'intrinsic')
        # path_prj_intri_out = os.path.join(path_prj_intri,'output')
        # intri_yml_intri = os.path.join(path_prj_intri_out,'intri.yml')

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_master_profile = os.path.join(path_addon, '0_calib_intri')
        current_profile = easymocap_properties.easymocap_intri_calib_list
        path_current_profile = os.path.join(path_master_profile, current_profile)
        intri_yml_profile = os.path.join(path_current_profile, 'intri.yml')
        extri_yml_profile = os.path.join(path_current_profile, 'extri.yml')

        intri_yml_extri = os.path.join(path_prj_extri_output, 'intri.yml')
        extri_yml_extri = os.path.join(path_prj_extri_output, 'extri.yml')

        calib_extri.calib_extri(path_prj_extri, intri_yml_profile)

        # copy intry to extri/output
        copyfile(intri_yml_profile, intri_yml_extri)
        copyfile(extri_yml_profile, extri_yml_extri)

        return {'FINISHED'}


class CheckCalibExtriCross(Operator):
    bl_idname = "easymocap.check_calib_extri_cross"
    bl_label = "Check Calibrate Extrinsic Cross"
    bl_description = "Check Calibrate Extrinsic Cross"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_extri = os.path.join(path_prj, 'extri')
        path_prj_out = os.path.join(path_prj_extri, 'output')

        path = path_prj_extri
        out = path_prj_out
        vis = True
        show = True
        debug = False
        cube = False
        grid = False
        calib = False

        if cube:
            points, lines = check_calib.load_cube()
            check_calib.check_scene(path, out, points, lines)
        elif grid:
            points, lines = check_calib.load_grid(xrange=15, yrange=14)
            check_calib.check_scene(path, out, points, lines)
        elif calib:
            check_calib.check_match(path, out)
        else:
            check_calib.check_calib(path, out, vis, show, debug)

        return {'FINISHED'}


class CheckCalibExtriCube(Operator):
    bl_idname = "easymocap.check_calib_extri_cube"
    bl_label = "Check Calibrate Extrinsic Cube"
    bl_description = "Check Calibrate Extrinsic Cube"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_extri = os.path.join(path_prj, 'extri')
        path_prj_out = os.path.join(path_prj_extri, 'output')

        path = path_prj_extri
        out = path_prj_out
        vis = False
        show = False
        debug = False
        cube = True
        grid = False
        calib = False

        if cube:
            points, lines = check_calib.load_cube()
            check_calib.check_scene(path, out, points, lines)
        elif grid:
            points, lines = check_calib.load_grid(xrange=15, yrange=14)
            check_calib.check_scene(path, out, points, lines)
        elif calib:
            check_calib.check_match(path, out)
        else:
            check_calib.check_calib(path, out, vis, show, debug)

        return {'FINISHED'}


class VideoExtractAndOpenposePass(Operator):
    bl_idname = "easymocap.video_extract_and_openpose_pass"
    bl_label = "Extract Video and Openpose Pass"
    bl_description = "Extract Video and Openpose Pass"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        openpose_path = easymocap_properties.easymocap_openpose_path
        openpose_render_bool = easymocap_properties.easymocap_bool_openpose_render
        openpose_hand_face_bool = easymocap_properties.easymocap_bool_openpose_hand_face

        path = path_prj
        mode = 'openpose'
        ext = 'jpg'
        annot = 'annots'
        highres = 1
        handface = openpose_hand_face_bool
        openpose = openpose_path
        render_flag = openpose_render_bool
        no2d = False
        start = 0
        end = 10000
        step = 1
        low = False
        gtbox = False
        debug = False
        path_origin = os.getcwd()

        if os.path.isdir(path):
            image_path = os.path.join(path, 'images')
            os.makedirs(image_path, exist_ok=True)
            subs_image = sorted(os.listdir(image_path))
            subs_videos = sorted(glob.glob(os.path.join(path, 'videos', '*.mp4')))
            if len(subs_videos) > len(subs_image):
                videos = sorted(glob.glob(os.path.join(path, 'videos', '*.mp4')))
                subs = []
                for video in videos:
                    basename = extract_video.extract_video(video, path, start=start, end=end, step=step)
                    subs.append(basename)
            else:
                subs = sorted(os.listdir(image_path))
            print('cameras: ', ' '.join(subs))
            if not no2d:
                for sub in subs:
                    image_root = os.path.join(path, 'images', sub)
                    annot_root = os.path.join(path, annot, sub)
                    if os.path.exists(annot_root):
                        # check the number of annots and images
                        if len(os.listdir(image_root)) == len(os.listdir(annot_root)):
                            print('skip ', annot_root)
                            continue
                    if mode == 'openpose':
                        extract_video.extract_2d(openpose, image_root,
                                                 os.path.join(path, 'openpose', sub),
                                                 os.path.join(path, 'openpose_render', sub), highres, handface,
                                                 render_flag)
                        extract_video.convert_from_openpose(
                            path_orig=path_origin,
                            src=os.path.join(path, 'openpose', sub),
                            dst=annot_root,
                            annotdir=annot
                        )
                    elif mode == 'yolo-hrnet':
                        extract_video.extract_yolo_hrnet(image_root, annot_root, ext, low)
        else:
            print(path, ' not exists')

        return {'FINISHED'}


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Triangulate(Operator):
    bl_idname = "easymocap.triangulate"
    bl_label = "Triangulate"
    bl_description = "Triangulate"

    def execute(self, context):

        easymocap_properties = context.scene.easymocap_prop
        path_prj = easymocap_properties.easymocap_prj_path
        qty_cam = easymocap_properties.easymocap_qty_cameras
        path_prj_out = os.path.join(path_prj, 'output')

        # path_prj_intri = os.path.join(path_prj,'intrinsic')
        # path_prj_intri_out = os.path.join(path_prj_intri,'output')
        # intri_yml_intri = os.path.join(path_prj_intri_out,'intri.yml')
        # extri_yml_intri = os.path.join(path_prj_intri_out,'extri.yml')

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_master_profile = os.path.join(path_addon, '0_calib_intri')
        current_profile = easymocap_properties.easymocap_intri_calib_list
        path_current_profile = os.path.join(path_master_profile, current_profile)
        intri_yml_profile = os.path.join(path_current_profile, 'intri.yml')
        extri_yml_profile = os.path.join(path_current_profile, 'extri.yml')

        intri_yml_prj = os.path.join(path_prj, 'intri.yml')
        extri_yml_prj = os.path.join(path_prj, 'extri.yml')

        # copy intry to extri/output
        copyfile(intri_yml_profile, intri_yml_prj)
        copyfile(extri_yml_profile, extri_yml_prj)

        # limpando a pasta keypoints3d, caso se va gerar dados separadamente trecho por trecho
        path_prj_out_keypoints3d = os.path.join(path_prj, 'output', 'keypoints3d')
        if os.path.exists(path_prj_out_keypoints3d):
            rmtree(path_prj_out_keypoints3d)

        sub = []
        if not easymocap_properties.easymocap_bool_custom_cameras:
            for i in range(qty_cam):  # cria a lista com a quantidade de cameras selecionadas na config
                cam = '{:02d}'.format(i + 1)
                sub.append(cam)
        else:
            cams = easymocap_properties.easymocap_str_custom_cameras
            cam_replace = cams.replace(' ', '')
            cams_split = cam_replace.split(',')
            for i in range(len(cams_split)):  # cria a lista com a quantidade de cameras selecionadas na config
                cam = '{:02d}'.format(int(cams_split[i]))
                sub.append(cam)

        path = path_prj
        out = path_prj_out
        cfg = None
        camera = None
        annot = 'annots'
        # sub = ['01','02']
        # sub = []
        from_file = None
        pid = [0]
        max_person = -1
        if easymocap_properties.easymocap_bool_start_end_option:
            start = easymocap_properties.easymocap_triang_start_frame
            end = easymocap_properties.easymocap_triang_end_frame
        else:
            start = 0
            end = 100000
        step = 1

        cfg_model = None
        gender = 'male'
        # write_smpl_full = False #esse e o que exporta dados de maos
        write_smpl_full = easymocap_properties.easymocap_bool_write_full_smpl

        if write_smpl_full:
            body = 'bodyhandface'
            model = 'smplx'
        else:
            body = 'body25'
            model = 'smpl'

        thres2d = 0.3

        smooth3d = 0
        MAX_REPRO_ERROR = 50
        MAX_SPEED_ERROR = 50
        robust3d = False

        vis_det = easymocap_properties.easymocap_bool_vis_det
        vis_repro = easymocap_properties.easymocap_bool_vis_repro
        vis_smpl = easymocap_properties.easymocap_bool_vis_smpl
        # vis_det = False
        # vis_repro =False
        # vis_smpl = False
        # print('write_smpl_full: ',write_smpl_full)
        write_vertices = False
        vis_mask = False
        undis = True
        sub_vis = []
        # sub_vis = [1,2]

        verbose = False
        save_origin = False
        restart = False
        no_opt = False
        debug = False
        opts = {}
        cfg_opts = []
        skel = False

        # args = Namespace(path=path,out=out,sub=sub,model=model,gender=gender,body=body, annot=annot,
        #         undis=undis, verbose=verbose, skel=skel, save_origin=save_origin,start=start,end=end,
        #         vis_smpl=vis_smpl, vis_repro=vis_repro, write_smpl_full=write_smpl_full,
        #         write_vertices=write_vertices, sub_vis=sub_vis, opts=opts, robust3d=robust3d)

        args = Namespace(path=path, out=out, cfg=cfg, camera=camera, annot=annot, sub=sub, from_file=from_file, pid=pid,
                         max_person=max_person, start=start, end=end, step=step,
                         cfg_model=cfg_model, body=body, model=model, gender=gender,
                         thres2d=thres2d,
                         smooth3d=smooth3d, MAX_REPRO_ERROR=MAX_REPRO_ERROR, MAX_SPEED_ERROR=MAX_SPEED_ERROR,
                         robust3d=robust3d,
                         vis_det=vis_det, vis_repro=vis_repro, vis_smpl=vis_smpl, write_smpl_full=write_smpl_full,
                         write_vertices=write_vertices, vis_mask=vis_mask, undis=undis, sub_vis=sub_vis,
                         verbose=verbose, save_origin=save_origin, restart=restart, no_opt=no_opt, debug=debug,
                         opts=opts, cfg_opts=cfg_opts, skel=skel)

        from .easymocap.mytools import load_parser, parse_parser
        from .easymocap.dataset import CONFIG, MV1PMF
        # parser = load_parser()
        # parser.add_argument('--skel', action='store_true')
        # args = parse_parser(parser)
        help = """
    Demo code for multiple views and one person:

        - Input : {} => {}
        - Output: {}
        - Body  : {}=>{}, {}
    """.format(args.path, ', '.join(args.sub), args.out, args.model, args.gender, args.body)
        # .format(path, ', '.join(sub), out, model, gender, body)
        # .format(args.path, ', '.join(args.sub), args.out, args.model, args.gender, args.body)
        print(help)
        skel_path = join(out, 'keypoints3d')
        dataset = MV1PMF(path, annot_root=annot, cams=sub, out=out,
                         config=CONFIG[body], kpts_type=body,
                         undis=undis, no_img=False, verbose=verbose)
        dataset.writer.save_origin = save_origin

        # if args.skel or not os.path.exists(skel_path):
        if skel or not os.path.exists(skel_path):
            mv1p.mv1pmf_skel(dataset, check_repro=True, args=args)
            # mv1p.mv1pmf_skel(dataset, check_repro=True, args=None)
        mv1p.mv1pmf_smpl(dataset, args)
        # mv1p.mv1pmf_smpl(dataset, skel, start, end, model, gender, verbose, vis_smpl, vis_repro, write_smpl_full, write_vertices,sub_vis,opts,robust3d, weight_pose=None, weight_shape=None)
        # mv1p.mv1pmf_smpl(dataset, skel, start, end, gender, vis_smpl, vis_repro, write_smpl_full, write_vertices,sub_vis,arg, weight_pose=None, weight_shape=None)

        return {'FINISHED'}


class TriangulateSimple(Operator):
    bl_idname = "easymocap.triangulate_simple"
    bl_label = "Triangulate"
    bl_description = "Triangulate"

    def execute(self, context):
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')

        result = subprocess.call([python_exe, "apps/demo/mv1p.py",
                                  "0_input/blender_mocap", "--out", "0_input/blender_mocap/output", "--undis",
                                  "--sub_vis", "1", "2"], shell=True)

        print("resultado: ", result)

        return {'FINISHED'}


class ImportSMPL(Operator, ImportHelper):
    bl_idname = "easymocap.import_smpl"
    bl_label = "Import SMPL Model"
    bl_description = "Import SMPL Model"

    filename_ext = ".pkl"
    filter_glob: StringProperty(
        default="*.pkl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_smpl = os.path.join(path_addon, 'data', 'smplx', 'smpl')
        if not os.path.exists(path_smpl):
            os.makedirs(path_smpl)

        smpl_model = easymocap_properties.easymocap_smpl_model_import

        src = self.filepath
        dst = os.path.join(path_smpl, smpl_model)

        copyfile(src, dst)
        return {'FINISHED'}


class ImportSMPLX(Operator, ImportHelper):
    bl_idname = "easymocap.import_smplx"
    bl_label = "Import SMPLX Model"
    bl_description = "Import SMPLX Model"

    filename_ext = ".pkl"
    filter_glob: StringProperty(
        default="*.pkl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_smplx = os.path.join(path_addon, 'data', 'smplx', 'smplx')
        if not os.path.exists(path_smplx):
            os.makedirs(path_smplx)

        smplx_model = easymocap_properties.easymocap_smplx_model_import

        src = self.filepath
        dst = os.path.join(path_smplx, smplx_model)

        copyfile(src, dst)
        return {'FINISHED'}


class NextUI(Operator):
    bl_idname = "easymocap.next_ui"
    bl_label = "Next UI"
    bl_description = "Next UI"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        if int(easymocap_properties.easymocap_ui) < 2:
            easymocap_properties.easymocap_ui = str(int(easymocap_properties.easymocap_ui) + 1)

        return {'FINISHED'}


class LastUI(Operator):
    bl_idname = "easymocap.last_ui"
    bl_label = "Last UI"
    bl_description = "Last UI"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        if int(easymocap_properties.easymocap_ui) > 0:
            easymocap_properties.easymocap_ui = str(int(easymocap_properties.easymocap_ui) - 1)

        return {'FINISHED'}


class CopyIntriExtriFromSlctdPrjToExtriOut(Operator):
    bl_idname = "easymocap.copy_intri_extri_from_slect_prj_to_extri_out"
    bl_label = "Copy the Intri and Extri data from selected project to extri out"
    bl_description = "Copy the Intri and Extri data from selected project to extri out"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

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

        copyfile(intri_calib_slctd, intri_extri_out)
        copyfile(extri_calib_slctd, extri_extri_out)
        return {'FINISHED'}


class ClearExtractAndOpenPose(Operator):
    bl_idname = "easymocap.clear_extract_and_openpose"
    bl_label = "Clear Image Extraction from video and OpenPose data"
    bl_description = "Clear Image Extraction from video and OpenPose data"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        openpose_clear = easymocap_properties.easymocap_openpose_clear

        path_prj = easymocap_properties.easymocap_prj_path

        path_prj_annots = os.path.join(path_prj, 'annots')
        path_prj_openpose = os.path.join(path_prj, 'openpose')
        path_prj_openpose_render = os.path.join(path_prj, 'openpose_render')
        path_prj_images = os.path.join(path_prj, 'images')

        if openpose_clear == 'annot':
            if os.path.exists(path_prj_annots):
                rmtree(path_prj_annots)
        elif openpose_clear == 'annot_openpose':
            if os.path.exists(path_prj_annots):
                rmtree(path_prj_annots)
            if os.path.exists(path_prj_openpose):
                rmtree(path_prj_openpose)
            if os.path.exists(path_prj_openpose_render):
                rmtree(path_prj_openpose_render)
        elif openpose_clear == 'annot_openpose_images':
            if os.path.exists(path_prj_annots):
                rmtree(path_prj_annots)
            if os.path.exists(path_prj_openpose):
                rmtree(path_prj_openpose)
            if os.path.exists(path_prj_openpose_render):
                rmtree(path_prj_openpose_render)
            if os.path.exists(path_prj_images):
                rmtree(path_prj_images)
        return {'FINISHED'}


class ClearTriangOutput(Operator):
    bl_idname = "easymocap.clear_triang_output"
    bl_label = "Clear Triangulation Output"
    bl_description = "Clear Triangulation Output"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop
        openpose_clear = easymocap_properties.easymocap_openpose_clear

        path_prj = easymocap_properties.easymocap_prj_path
        path_prj_ouput = os.path.join(path_prj, 'output')

        if os.path.exists(path_prj_ouput):
            rmtree(path_prj_ouput)

        return {'FINISHED'}


class RemoveSMPLModel(Operator):
    bl_idname = "easymocap.remove_smpl_model"
    bl_label = "Remove SMPL Model"
    bl_description = "Remove SMPL Model"

    def execute(self, context):
        path_addon = os.path.dirname(os.path.abspath(__file__))
        path_smpl_model = os.path.join(path_addon, 'data', 'smplx', 'smpl')

        if os.path.exists(path_smpl_model):
            rmtree(path_smpl_model)

        return {'FINISHED'}


class NextCam(Operator):
    bl_idname = "easymocap.next_cam"
    bl_label = "Next Cam"
    bl_description = "Next Cam"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        # qty_cameras = easymocap_properties.easymocap_qty_cameras
        easymocap_properties.easymocap_cameras_list = str(int(slct_cam) + 1)

        return {'FINISHED'}


class PrevCam(Operator):
    bl_idname = "easymocap.prev_cam"
    bl_label = "Previus Cam"
    bl_description = "Previous Cam"

    def execute(self, context):
        easymocap_properties = context.scene.easymocap_prop

        slct_cam = easymocap_properties.easymocap_cameras_list
        # qty_cameras = easymocap_properties.easymocap_qty_cameras
        easymocap_properties.easymocap_cameras_list = str(int(slct_cam) - 1)

        return {'FINISHED'}


class NoActionButton(Operator):
    bl_idname = "easymocap.no_action_buttom"
    bl_label = "No action"
    bl_description = "No Action"

    def execute(self, context):
        print('no action')

        return {'FINISHED'}