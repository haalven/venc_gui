#! /Users/xhalc/python-venv/.venv/bin/python3

import os
import shlex
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QSlider,
    QFileDialog, QHBoxLayout, QVBoxLayout, QGridLayout
)


VIDEO_FILTER = 'Video files (*.mp4 *.m4v *.mpg *.mpeg *.qt *.avi);;All files (*)'


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FFmpeg VideoToolbox command builder')
        self.setMinimumWidth(720)

        # --- Input file picker ---
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        self.browse_btn = QPushButton('Browse…')
        self.browse_btn.clicked.connect(self.pick_file)

        # --- Codec dropdown ---
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(['HEVC (h265)', 'AVC (h264)'])
        self.codec_combo.setCurrentIndex(0)
        self.codec_combo.currentIndexChanged.connect(self.update_command)

        # --- Resize controls ---
        self.resize_x_edit = QLineEdit('12080')
        self.resize_y_edit = QLineEdit('720')
        self.resize_x_edit.textChanged.connect(self.update_command)
        self.resize_y_edit.textChanged.connect(self.update_command)

        # --- Quality slider (1..100, default 66) ---
        self.q_slider = QSlider(Qt.Orientation.Horizontal)
        self.q_slider.setRange(1, 100)
        self.q_slider.setValue(66)
        self.q_slider.valueChanged.connect(self.update_quality_label_and_command)

        self.q_label = QLabel('66')
        self.q_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.q_hint = QLabel('Quality (1–100)')
        self.q_hint.setStyleSheet('color: #555;')

        # --- Audio dropdown ---
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(['copy audio', 'AAC', 'no audio'])
        self.audio_combo.setCurrentIndex(0)
        self.audio_combo.currentIndexChanged.connect(self.update_command)

        # --- Command field + copy button ---
        self.cmd_edit = QLineEdit()
        self.cmd_edit.setReadOnly(True)
        self.copy_btn = QPushButton('Copy')
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        # Layout
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel('Input video'), 0, 0)
        inp_row = QHBoxLayout()
        inp_row.addWidget(self.input_edit, 1)
        inp_row.addWidget(self.browse_btn)
        grid.addLayout(inp_row, 0, 1)

        grid.addWidget(QLabel('Resize (x, y)'), 1, 0)
        resize_row = QHBoxLayout()
        resize_row.addWidget(self.resize_x_edit)
        resize_row.addWidget(QLabel('x'))
        resize_row.addWidget(self.resize_y_edit)
        grid.addLayout(resize_row, 1, 1)

        grid.addWidget(QLabel('Video codec'), 2, 0)
        grid.addWidget(self.codec_combo, 2, 1)

        q_row = QHBoxLayout()
        q_row.addWidget(self.q_slider, 1)
        q_row.addWidget(self.q_label)
        q_box = QVBoxLayout()
        q_box.addWidget(self.q_hint)
        q_box.addLayout(q_row)
        grid.addWidget(QLabel('Video quality'), 3, 0)
        grid.addLayout(q_box, 3, 1)

        grid.addWidget(QLabel('Audio option'), 4, 0)
        grid.addWidget(self.audio_combo, 4, 1)

        bottom = QHBoxLayout()
        bottom.addWidget(self.cmd_edit, 1)
        bottom.addWidget(self.copy_btn)

        root = QVBoxLayout()
        root.addLayout(grid)
        root.addSpacing(8)
        root.addWidget(QLabel('FFmpeg command:'))
        root.addLayout(bottom)

        self.setLayout(root)

        self.update_command()

    def pick_file(self):
        start_dir = os.path.expanduser('~/Downloads')
        path, _ = QFileDialog.getOpenFileName(self, 'Choose a video file', start_dir, VIDEO_FILTER)
        if path:
            self.input_edit.setText(path)
            self.update_command()

    def update_quality_label_and_command(self, val: int):
        self.q_label.setText(str(val))
        self.update_command()

    @staticmethod
    def q(path: str) -> str:
        # Quote safely for a shell command display.
        return shlex.quote(path)

    def build_output_path(self, input_path: str) -> str:
        # Spec: output path is inputpath + '.videotoolbox.mp4'
        return input_path + '.videotoolbox.mp4'

    def update_command(self):
        inp = self.input_edit.text().strip()
        if not inp:
            self.cmd_edit.setText('')
            return

        qv = self.q_slider.value()
        resize_x = self.resize_x_edit.text().strip() or '12080'
        resize_y = self.resize_y_edit.text().strip() or '720'
        scale_filter = f'scale_vt=w={resize_x}:h={resize_y}'

        # Video codec
        if self.codec_combo.currentText().startswith('AVC'):
            v_opts = ['-c:v', 'h264_videotoolbox']
        else:
            v_opts = ['-c:v', 'hevc_videotoolbox', '-tag:v', 'hvc1']

        # Audio options
        a_choice = self.audio_combo.currentText()
        if a_choice == 'no audio':
            a_opts = ['-an']
        elif a_choice == 'AAC':
            a_opts = ['-c:a', 'aac_at']
        else:
            a_opts = ['-c:a', 'copy']

        outp = self.build_output_path(inp)

        cmd = [
            'ffmpeg',
            '-hwaccel', 'videotoolbox',
            '-hwaccel_output_format', 'videotoolbox_vld',
            '-i', inp,
            '-vf', scale_filter,
            *v_opts,
            '-q:v', str(qv),
            *a_opts,
            outp,
        ]
        cmd_str = (
            f'ffmpeg -hwaccel videotoolbox -hwaccel_output_format videotoolbox_vld -i {self.q(inp)} '
            f'-vf {self.q(scale_filter)} '
            + ' '.join(v_opts)
            + f' -q:v {qv} '
            + ' '.join(a_opts)
            + f' {self.q(outp)}'
        )

        self.cmd_edit.setText(cmd_str)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.cmd_edit.text().strip()) # type: ignore


def main():
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
