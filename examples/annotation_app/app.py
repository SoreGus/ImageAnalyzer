from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

try:
    from .exporter import (
        export_bundle,
        export_json,
        render_annotated_image,
        with_colors,
    )
except ImportError:
    from exporter import (
        export_bundle,
        export_json,
        render_annotated_image,
        with_colors,
    )


ROOT = Path(__file__).resolve().parent
IMAGES_DIR = ROOT / "images"
ANNOTATIONS_DIR = ROOT / "sample_annotations"
OUTPUTS_DIR = ROOT / "outputs" / "describe"


class AnnotationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ImageAnalyzer Annotation Export Example")
        self.root.geometry("1180x780")
        self.root.minsize(900, 640)

        self.image_paths = sorted(IMAGES_DIR.glob("*.png"))

        if not self.image_paths:
            raise RuntimeError(
                f"No sample images found in {IMAGES_DIR}"
            )

        self.index = 0
        self.annotation: dict[str, Any] = {}

        self.photo: ImageTk.PhotoImage | None = None
        self.preview_size = (1, 1)
        self.preview_offset = (0, 0)

        self.analyzer: Any | None = None
        self.analysis_running = False

        self._build_ui()
        self.load_current_sample()

    @property
    def image_path(self) -> Path:
        return self.image_paths[self.index]

    @property
    def sample_annotation_path(self) -> Path:
        return ANNOTATIONS_DIR / f"{self.image_path.stem}.json"

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(
            self.root,
            padding=8,
        )

        toolbar.pack(fill=tk.X)

        self.previous_button = ttk.Button(
            toolbar,
            text="Previous",
            command=self.previous,
        )

        self.previous_button.pack(side=tk.LEFT)

        self.next_button = ttk.Button(
            toolbar,
            text="Next",
            command=self.next,
        )

        self.next_button.pack(
            side=tk.LEFT,
            padx=(6, 12),
        )

        self.load_sample_button = ttk.Button(
            toolbar,
            text="Load Sample",
            command=self.load_current_sample,
        )

        self.load_sample_button.pack(side=tk.LEFT)

        self.analyze_button = ttk.Button(
            toolbar,
            text="Analyze Current",
            command=self.analyze_current,
        )

        self.analyze_button.pack(
            side=tk.LEFT,
            padx=6,
        )

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL,
        ).pack(
            side=tk.LEFT,
            fill=tk.Y,
            padx=8,
        )

        ttk.Button(
            toolbar,
            text="Export JSON",
            command=self.export_json_only,
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="Export Annotated Image",
            command=self.export_image_only,
        ).pack(
            side=tk.LEFT,
            padx=6,
        )

        ttk.Button(
            toolbar,
            text="Export Both",
            command=self.export_current,
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="Export All Samples",
            command=self.export_all_samples,
        ).pack(
            side=tk.LEFT,
            padx=6,
        )

        self.progress = ttk.Progressbar(
            toolbar,
            mode="indeterminate",
            length=100,
        )

        self.progress.pack(
            side=tk.RIGHT,
            padx=(8, 0),
        )

        self.progress.pack_forget()

        self.status = ttk.Label(
            toolbar,
            text="",
        )

        self.status.pack(side=tk.RIGHT)

        paned = ttk.Panedwindow(
            self.root,
            orient=tk.HORIZONTAL,
        )

        paned.pack(
            fill=tk.BOTH,
            expand=True,
        )

        preview_frame = ttk.Frame(
            paned,
            padding=(8, 0, 4, 8),
        )

        json_frame = ttk.Frame(
            paned,
            padding=(4, 0, 8, 8),
        )

        paned.add(
            preview_frame,
            weight=3,
        )

        paned.add(
            json_frame,
            weight=2,
        )

        self.canvas = tk.Canvas(
            preview_frame,
            background="#202124",
            highlightthickness=0,
        )

        self.canvas.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.canvas.bind(
            "<Configure>",
            lambda _: self.render_preview(),
        )

        ttk.Label(
            json_frame,
            text="Export JSON preview",
        ).pack(
            anchor=tk.W,
            pady=(0, 6),
        )

        self.json_text = tk.Text(
            json_frame,
            wrap=tk.NONE,
            font=("Menlo", 11),
        )

        self.json_text.pack(
            fill=tk.BOTH,
            expand=True,
        )

    def previous(self) -> None:
        if self.analysis_running:
            return

        self.index = (
            self.index - 1
        ) % len(self.image_paths)

        self.load_current_sample()

    def next(self) -> None:
        if self.analysis_running:
            return

        self.index = (
            self.index + 1
        ) % len(self.image_paths)

        self.load_current_sample()

    def load_current_sample(self) -> None:
        if self.analysis_running:
            return

        if not self.sample_annotation_path.exists():
            self.annotation = {
                "description": "",
                "elements": [],
                "relations": [],
            }
        else:
            payload = json.loads(
                self.sample_annotation_path.read_text(
                    encoding="utf-8"
                )
            )

            payload.pop(
                "source_image",
                None,
            )

            self.annotation = with_colors(
                payload
            )

        self.refresh()

        self.status.config(
            text=f"Sample: {self.image_path.name}"
        )

    def analyze_current(self) -> None:
        if self.analysis_running:
            return

        image_path = self.image_path

        self.analysis_running = True

        self.analyze_button.config(
            state=tk.DISABLED
        )

        self.previous_button.config(
            state=tk.DISABLED
        )

        self.next_button.config(
            state=tk.DISABLED
        )

        self.load_sample_button.config(
            state=tk.DISABLED
        )

        self.status.config(
            text=f"Analyzing: {image_path.name}"
        )

        self.progress.pack(
            side=tk.RIGHT,
            padx=(8, 0),
        )

        self.progress.start(10)

        thread = threading.Thread(
            target=self._analyze_worker,
            args=(image_path,),
            daemon=True,
        )

        thread.start()

    def _analyze_worker(
        self,
        image_path: Path,
    ) -> None:
        try:
            if self.analyzer is None:
                from image_analyzer import ImageAnalyzer

                self.root.after(
                    0,
                    self.status.config,
                    {
                        "text": "Loading model..."
                    },
                )

                self.analyzer = ImageAnalyzer()

            self.root.after(
                0,
                self.status.config,
                {
                    "text": f"Analyzing: {image_path.name}"
                },
            )

            result = self.analyzer.describe(
                image_path
            )

            annotation = with_colors(
                json.loads(
                    result.to_json()
                )
            )

            self.root.after(
                0,
                self._analysis_completed,
                image_path,
                annotation,
            )

        except Exception as error:
            self.root.after(
                0,
                self._analysis_failed,
                str(error),
            )

    def _analysis_completed(
        self,
        image_path: Path,
        annotation: dict[str, Any],
    ) -> None:
        self.annotation = annotation

        self.refresh()

        self.status.config(
            text=f"Analyzed: {image_path.name}"
        )

        self._finish_analysis_state()

    def _analysis_failed(
        self,
        error: str,
    ) -> None:
        self._finish_analysis_state()

        self.status.config(
            text="Analysis failed"
        )

        messagebox.showerror(
            "Analysis failed",
            error,
        )

    def _finish_analysis_state(self) -> None:
        self.analysis_running = False

        self.progress.stop()
        self.progress.pack_forget()

        self.analyze_button.config(
            state=tk.NORMAL
        )

        self.previous_button.config(
            state=tk.NORMAL
        )

        self.next_button.config(
            state=tk.NORMAL
        )

        self.load_sample_button.config(
            state=tk.NORMAL
        )

    def refresh(self) -> None:
        self.render_preview()
        self.render_json()

    def render_json(self) -> None:
        payload = with_colors(
            self.annotation
        )

        payload["source_image"] = (
            self.image_path.name
        )

        self.json_text.delete(
            "1.0",
            tk.END,
        )

        self.json_text.insert(
            "1.0",
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
        )

    def render_preview(self) -> None:
        canvas_width = max(
            1,
            self.canvas.winfo_width(),
        )

        canvas_height = max(
            1,
            self.canvas.winfo_height(),
        )

        with Image.open(self.image_path) as opened:
            source = opened.convert("RGB")

        scale = min(
            canvas_width / source.width,
            canvas_height / source.height,
        )

        width = max(
            1,
            round(source.width * scale),
        )

        height = max(
            1,
            round(source.height * scale),
        )

        preview = source.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

        self.photo = ImageTk.PhotoImage(
            preview
        )

        offset_x = (
            canvas_width - width
        ) // 2

        offset_y = (
            canvas_height - height
        ) // 2

        self.preview_size = (
            width,
            height,
        )

        self.preview_offset = (
            offset_x,
            offset_y,
        )

        self.canvas.delete("all")

        self.canvas.create_image(
            offset_x,
            offset_y,
            image=self.photo,
            anchor=tk.NW,
        )

        self._draw_boxes()

    def _draw_boxes(self) -> None:
        width, height = self.preview_size
        offset_x, offset_y = self.preview_offset

        elements = with_colors(
            self.annotation
        ).get(
            "elements",
            [],
        )

        for index, element in enumerate(elements):
            if not isinstance(element, dict):
                continue

            box = element.get(
                "bounding_box"
            )

            if not isinstance(box, dict):
                continue

            try:
                x0 = max(
                    0.0,
                    min(
                        1.0,
                        float(
                            box["x_min"]
                        ),
                    ),
                )

                y0 = max(
                    0.0,
                    min(
                        1.0,
                        float(
                            box["y_min"]
                        ),
                    ),
                )

                x1 = max(
                    0.0,
                    min(
                        1.0,
                        float(
                            box["x_max"]
                        ),
                    ),
                )

                y1 = max(
                    0.0,
                    min(
                        1.0,
                        float(
                            box["y_max"]
                        ),
                    ),
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            color = str(
                element.get(
                    "color",
                    "#FF0000",
                )
            )

            label = str(
                element.get(
                    "label",
                    f"element-{index + 1}",
                )
            )

            ax0 = (
                offset_x
                + min(x0, x1) * width
            )

            ay0 = (
                offset_y
                + min(y0, y1) * height
            )

            ax1 = (
                offset_x
                + max(x0, x1) * width
            )

            ay1 = (
                offset_y
                + max(y0, y1) * height
            )

            self.canvas.create_rectangle(
                ax0,
                ay0,
                ax1,
                ay1,
                outline=color,
                width=3,
            )

            text_id = self.canvas.create_text(
                ax0 + 5,
                max(
                    offset_y + 2,
                    ay0 - 6,
                ),
                text=label,
                fill="white",
                anchor=tk.SW,
            )

            bbox = self.canvas.bbox(
                text_id
            )

            if bbox:
                background = (
                    self.canvas.create_rectangle(
                        *bbox,
                        fill=color,
                        outline=color,
                    )
                )

                self.canvas.tag_lower(
                    background,
                    text_id,
                )

    def _paths(self) -> tuple[Path, Path]:
        stem = self.image_path.stem

        return (
            OUTPUTS_DIR
            / "json"
            / f"{stem}.json",
            OUTPUTS_DIR
            / "annotated"
            / f"{stem}_annotated.png",
        )

    def export_json_only(self) -> None:
        json_path, _ = self._paths()

        export_json(
            self.annotation,
            self.image_path,
            json_path,
        )

        self.status.config(
            text=(
                "Exported "
                f"{json_path.relative_to(ROOT)}"
            )
        )

    def export_image_only(self) -> None:
        _, image_path = self._paths()

        render_annotated_image(
            self.image_path,
            self.annotation,
            image_path,
        )

        self.status.config(
            text=(
                "Exported "
                f"{image_path.relative_to(ROOT)}"
            )
        )

    def export_current(self) -> None:
        json_path, image_path = (
            self._paths()
        )

        export_bundle(
            self.annotation,
            self.image_path,
            json_path,
            image_path,
        )

        self.status.config(
            text=f"Exported {self.image_path.stem}"
        )

    def export_all_samples(self) -> None:
        count = 0

        for image_path in self.image_paths:
            annotation_path = (
                ANNOTATIONS_DIR
                / f"{image_path.stem}.json"
            )

            if not annotation_path.exists():
                continue

            payload = json.loads(
                annotation_path.read_text(
                    encoding="utf-8"
                )
            )

            payload.pop(
                "source_image",
                None,
            )

            export_bundle(
                payload,
                image_path,
                OUTPUTS_DIR
                / "json"
                / f"{image_path.stem}.json",
                OUTPUTS_DIR
                / "annotated"
                / f"{image_path.stem}_annotated.png",
            )

            count += 1

        self.status.config(
            text=f"Exported {count} bundled samples"
        )


def main() -> None:
    root = tk.Tk()

    AnnotationApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()