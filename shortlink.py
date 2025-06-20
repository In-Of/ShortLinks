import os
import re
import sys
import shutil

CHARS = [str(i) for i in range(10)] + [chr(c) for c in range(ord('a'), ord('z')+1)]
REDIR_RE = re.compile(r'url=([^"]+)', re.IGNORECASE)

def next_code(existing_dirs):
    used = set(existing_dirs)
    for c1 in CHARS:
        for c2 in CHARS:
            code = c1 + c2
            if code not in used:
                return code
    print("Свободных кодов не осталось!")
    sys.exit(1)

def read_redirect(path):
    try:
        with open(os.path.join(path, "index.html"), "r", encoding="utf-8") as f:
            content = f.read()
        m = REDIR_RE.search(content)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""

def make_html(url):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={url}">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="{url}">{url}</a>...</p>
</body>
</html>
"""

def scan_links():
    dirs = [d for d in os.listdir() if os.path.isdir(d) and len(d) == 2 and all(c in CHARS for c in d)]
    links = []
    for d in dirs:
        url = read_redirect(d)
        links.append((d, os.path.join(d, "index.html"), url))
    links.sort(key=lambda x: (CHARS.index(x[0][0]), CHARS.index(x[0][1])))
    return links

def list_links(links):
    print("\nТекущие короткие ссылки:")
    print("-" * 64)
    print(f"{'№':<4} {'Код':<6} {'Длинная ссылка'}")
    print("-" * 64)
    for i, (code, _, url) in enumerate(links, 1):
        print(f"{i:<4} {code:<6} {url}")
    print("-" * 64)

def input_code(prompt, used=None):
    while True:
        code = input(prompt).strip().lower()
        if len(code) == 2 and all(c in CHARS for c in code):
            if used and code in used:
                print("Код уже используется. Выберите другой.")
                continue
            return code
        print("Некорректный код. Только два символа: 0-9, a-z.")

def create_link():
    links = scan_links()
    codes = [l[0] for l in links]
    new_code = next_code(codes)
    url = input(f"Введите длинную ссылку для {new_code}/index.html: ").strip()
    dir_path = new_code
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_html(url))
    print(f"Создано: {dir_path}/index.html → {url}")

def edit_link():
    links = scan_links()
    if not links:
        print("Нет ни одной короткой ссылки для редактирования.")
        return
    list_links(links)
    try:
        idx = int(input("Введите номер ссылки для редактирования: ")) - 1
        if not (0 <= idx < len(links)):
            print("Некорректный номер.")
            return
    except ValueError:
        print("Введите число.")
        return

    old_code, old_path, old_url = links[idx]
    print(f"Текущий код: {old_code}, ссылка: {old_url}")
    codes_in_use = set(l[0] for l in links if l[0] != old_code)
    new_code = input_code("Новый код (Enter — не менять): ", used=codes_in_use) or old_code
    new_url = input("Новая длинная ссылка (Enter — не менять): ").strip() or old_url

    # Переименовать каталог, если код изменился
    if new_code != old_code:
        new_dir = new_code
        if os.path.exists(new_dir):
            print("Целевая папка уже существует.")
            return
        os.rename(old_code, new_code)
    else:
        new_dir = old_code

    with open(os.path.join(new_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_html(new_url))
    print(f"Ссылка обновлена: {new_dir}/index.html → {new_url}")

def export_links(filepath="links.txt"):
    links = scan_links()
    with open(filepath, "w", encoding="utf-8") as f:
        for code, _, url in links:
            f.write(f"s.lifebalance.ru/{code}/ -> {url}\n")
    print(f"Актуальные ссылки сохранены в {filepath}")

def main():
    while True:
        print("\nМеню:")
        print("1. Создать новую короткую ссылку")
        print("2. Редактировать существующую ссылку")
        print("3. Показать все ссылки")
        print("0. Выйти")
        cmd = input("Выберите действие: ").strip()
        if cmd == '1':
            create_link()
        elif cmd == '2':
            edit_link()
        elif cmd == '3':
            links = scan_links()
            list_links(links)
        elif cmd == '0':
            export_links()
            print("Выход.")
            break
        else:
            print("Некорректный ввод.")

if __name__ == "__main__":
    main()
