# 画像キャプション付与ツール

画像の**中央下**に「施策名 名前」を入れるツールです。  
テキストは太字・#565CAA・白背景で描画されます。

- **ブラウザ版**: このリポジトリを GitHub Pages で公開すると、URL を開くだけで使えます。
- **Python 版**: ローカルで一括処理したい場合は [add_caption_to_images.py](add_caption_to_images.py) を利用してください。

---

## ブラウザ版の使い方（GitHub Pages）

1. GitHub で **新しいリポジトリ**を作成（例: `image-caption-tool`）
2. このフォルダの中身を push する:
   ```bash
   cd image-caption-tool
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
   git push -u origin main
   ```
3. リポジトリの **Settings → Pages** を開く
4. **Source** で「Deploy from a branch」を選び、Branch を `main`、Folder を **/ (root)** にして Save
5. 数分後、`https://<あなたのユーザー名>.github.io/<リポジトリ名>/` でツールが開きます

**注意**: 処理はすべてブラウザ内で完結します。画像は外部に送信されません。

---

## Python 版の使い方

```bash
pip install Pillow
python add_caption_to_images.py "施策名" ./画像フォルダ
```

- フォルダを渡すと配下の全階層の画像を**上書き**します（ファイル名はそのまま）
- 名前のデフォルトは「佐藤貴子」。変更する場合は `--name "名前"` を付けてください

詳細は [README_image_caption.md](README_image_caption.md) を参照してください。
