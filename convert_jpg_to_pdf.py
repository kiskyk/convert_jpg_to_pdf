import threading
import tkinter as tk
from pathlib import Path
from subprocess import run
from tkinter import filedialog, messagebox

import img2pdf


class Application(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=500, height=300, borderwidth=4, relief="groove")
        self.root = root
        self.pack()
        self.pack_propagate(0)

        self.file_paths = []

        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(side="bottom", pady=10)

        self.select_btn = tk.Button(
            btn_frame, text="ファイル選択", command=self.select_folder, width=10
        )
        self.select_btn.pack(side="left", padx=10)

        self.submit_btn = tk.Button(
            btn_frame, text="実行", command=self.start_conversion_thread, width=10
        )
        self.submit_btn.pack(side="left", padx=10)

        quit_btn = tk.Button(
            btn_frame, text="閉じる", command=self.root.destroy, width=10
        )
        quit_btn.pack(side="left", padx=10)

    def select_folder(self):
        self.file_paths = filedialog.askopenfilenames(
            title="PDFに変換するファイルを選択",
            filetypes=[("JPEG files", "*.jpg *.jpeg")],
        )
        if self.file_paths:
            text = "選択されたファイル:\n" + "\n".join(
                [Path(f).name for f in self.file_paths]
            )
            messagebox.showinfo("通知", text)
        else:
            print("ファイルが選択されませんでした。")

    def start_conversion_thread(self):
        if not self.file_paths:
            messagebox.showwarning("警告", "先に変換するファイルを選択してください。")
            return

        # ボタンを一時的に無効化して連打を防止
        self.submit_btn.config(state="disabled")
        self.select_btn.config(state="disabled")

        # 別スレッドで convert_jpg_to_pdf を実行
        thread = threading.Thread(target=self.convert_jpg_to_pdf)
        thread.start()

    def convert_jpg_to_pdf(self):
        # 保存先（Downloadsフォルダ内の output.pdf）
        output_dir = Path.home() / "Downloads"
        output_file = output_dir / "output.pdf"

        try:
            # img2pdfを使って選択された画像を1つのPDFに結合
            with output_file.open(mode="wb") as f:
                f.write(img2pdf.convert(self.file_paths))

        except Exception as e:
            self.root.after(
                0, messagebox.showerror, "エラー", f"変換中にエラーが発生しました:\n{e}"
            )

        finally:
            # 完了処理をメインスレッドに戻して実行（Path.home()のカッコ忘れも修正）
            self.root.after(0, self.open_explorer, output_dir)

    def open_explorer(self, path):
        # ボタンを有効化して元の状態に戻す
        self.submit_btn.config(state="normal")
        self.select_btn.config(state="normal")
        # 選択されたファイルリストをリセット
        self.file_paths = []

        ret = messagebox.askyesno(
            "確認", "すべてのファイルの変換が終了しました。\n保存場所を開きますか？"
        )
        if ret:
            run(["explorer", str(path)])


if __name__ == "__main__":
    root = tk.Tk()
    root.title("jpgからpdf変換ツール")
    root.geometry("300x100")
    app = Application(root=root)
    app.mainloop()
