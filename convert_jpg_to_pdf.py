import threading
import tkinter as tk
from pathlib import Path
from subprocess import run
from tkinter import filedialog, messagebox, ttk

import img2pdf
from tkinterdnd2 import DND_FILES, TkinterDnD

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")


class Application(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=520, height=420)
        self.root = root
        self.pack(fill="both", expand=True)
        self.pack_propagate(0)

        self.file_paths: list[str] = []
        self.output_path_var = tk.StringVar(
            value=str(Path.home() / "Downloads" / "output.pdf")
        )
        self.status_var = tk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        # --- ファイルリスト + 操作ボタン ---
        list_frame = tk.Frame(self)
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 5))

        list_container = tk.Frame(list_frame)
        list_container.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_container, orient="vertical")
        self.listbox = tk.Listbox(
            list_container,
            selectmode="extended",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.on_drop)

        list_btn_frame = tk.Frame(list_frame)
        list_btn_frame.pack(side="left", fill="y", padx=(8, 0))

        tk.Button(
            list_btn_frame, text="追加", width=8, command=self.select_files
        ).pack(pady=2)
        tk.Button(
            list_btn_frame, text="上へ", width=8, command=self.move_up
        ).pack(pady=2)
        tk.Button(
            list_btn_frame, text="下へ", width=8, command=self.move_down
        ).pack(pady=2)
        tk.Button(
            list_btn_frame, text="削除", width=8, command=self.remove_selected
        ).pack(pady=2)
        tk.Button(
            list_btn_frame, text="クリア", width=8, command=self.clear_all
        ).pack(pady=2)

        # --- 出力先指定 ---
        output_frame = tk.Frame(self)
        output_frame.pack(side="top", fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="出力先:").pack(side="left")
        tk.Entry(
            output_frame, textvariable=self.output_path_var, state="readonly"
        ).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(
            output_frame, text="参照...", command=self.select_output_path
        ).pack(side="left")

        # --- 進捗表示 ---
        progress_frame = tk.Frame(self)
        progress_frame.pack(side="top", fill="x", padx=10, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(side="top", fill="x")
        tk.Label(progress_frame, textvariable=self.status_var, anchor="w").pack(
            side="top", fill="x"
        )

        # --- 実行ボタン群 ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(side="bottom", pady=10)

        self.submit_btn = tk.Button(
            btn_frame, text="実行", command=self.start_conversion_thread, width=10
        )
        self.submit_btn.pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="閉じる", command=self.root.destroy, width=10
        ).pack(side="left", padx=10)

    # --- ファイルリスト操作 ---
    def add_files(self, paths):
        added = 0
        skipped = 0
        existing = {str(Path(p).resolve()) for p in self.file_paths}

        for p in paths:
            path = Path(p)
            if path.suffix.lower() not in IMAGE_SUFFIXES:
                skipped += 1
                continue
            resolved = str(path.resolve())
            if resolved in existing:
                continue
            existing.add(resolved)
            self.file_paths.append(str(path))
            self.listbox.insert("end", path.name)
            added += 1

        if skipped:
            messagebox.showwarning(
                "警告", f"{skipped}件の対応外のファイルはスキップされました。"
            )
        if added:
            self.status_var.set(f"{added}件のファイルを追加しました。")

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="PDFに変換するファイルを選択",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")],
        )
        if paths:
            self.add_files(paths)

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self.add_files(paths)

    def remove_selected(self):
        for index in reversed(self.listbox.curselection()):
            self.listbox.delete(index)
            del self.file_paths[index]

    def clear_all(self):
        self.listbox.delete(0, "end")
        self.file_paths.clear()
        self.status_var.set("")

    def move_up(self):
        for index in self.listbox.curselection():
            if index == 0:
                continue
            self._swap(index, index - 1)

    def move_down(self):
        for index in reversed(self.listbox.curselection()):
            if index == self.listbox.size() - 1:
                continue
            self._swap(index, index + 1)

    def _swap(self, i, j):
        self.file_paths[i], self.file_paths[j] = self.file_paths[j], self.file_paths[i]

        text_i, text_j = self.listbox.get(i), self.listbox.get(j)
        self.listbox.delete(i)
        self.listbox.insert(i, text_j)
        self.listbox.delete(j)
        self.listbox.insert(j, text_i)

        for idx in (i, j):
            self.listbox.selection_set(idx)

    # --- 出力先選択 ---
    def select_output_path(self):
        current = Path(self.output_path_var.get())
        path = filedialog.asksaveasfilename(
            title="保存先を選択",
            initialdir=current.parent,
            initialfile=current.name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if path:
            self.output_path_var.set(path)

    # --- 変換処理 ---
    def start_conversion_thread(self):
        if not self.file_paths:
            messagebox.showwarning("警告", "先に変換するファイルを選択してください。")
            return

        self.submit_btn.config(state="disabled")
        self.status_var.set("変換中...")
        self.progress_bar.start(10)

        thread = threading.Thread(target=self.convert_jpg_to_pdf)
        thread.start()

    def convert_jpg_to_pdf(self):
        output_file = Path(self.output_path_var.get())
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with output_file.open(mode="wb") as f:
                f.write(img2pdf.convert(self.file_paths))
            self.root.after(0, self.on_conversion_done, output_file)
        except Exception as e:
            self.root.after(
                0, messagebox.showerror, "エラー", f"変換中にエラーが発生しました:\n{e}"
            )
            self.root.after(0, self.reset_state)

    def on_conversion_done(self, output_file):
        self.reset_state()
        ret = messagebox.askyesno(
            "確認", "すべてのファイルの変換が終了しました。\n保存場所を開きますか？"
        )
        if ret:
            run(["explorer", "/select,", str(output_file)])

    def reset_state(self):
        self.progress_bar.stop()
        self.submit_btn.config(state="normal")
        self.status_var.set("")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title("jpgからpdf変換ツール")
    root.geometry("520x420")
    root.minsize(420, 360)
    app = Application(root=root)
    app.mainloop()
