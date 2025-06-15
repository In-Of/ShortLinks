import os
import re
import sys

# Список допустимых символов
CHARS = [str(i) for i in range(10)] + [chr(c) for c in range(ord('a'), ord('z')+1)]
EXT = ".htm"
REDIR_RE = re.compile(r'url=([^"]+)', re.IGNORECASE)

def next_code(existing):
    """Вычисляет следующий свободный 2-символьный код."""
    used = set(f[:-4] for f in existing if len(f) == 6 and f.endswith(EXT))
    for c1 in CHARS:
        for c2 in CHARS:
            code = c1 + c2
            if code not in used:
                return code
    print("Свободных кодов не осталось!")
    sys.exit(1)

def read_redirect(filepath):
    """Читает длинную ссылку из meta-редиректа html."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
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
    """Сканирует директорию и возвращает [(код, filename, url)]"""
    files = [f for f in os.listdir() if f.endswith(EXT) and len(f) == 6]
    links = []
    for f in files:
        code = f[:-4]
        url = read_redirect(f)
        links.append((code, f, url))
    # сортировка по коду
    links.sort(key=lambda x: (CHARS.index(x[0][0]), CHARS.index(x[0][1])))
    return links

def list_links(links):
    print("\nТекущие короткие ссылки:")
    print("-" * 64)
    print(f"{'№':<4} {'Код':<6} {'Длинная ссылка'}")
    print("-" * 64)
    for i, (code, fname, url) in enumerate(links, 1):
        print(f"{i:<4} {fname:<6} {url}")
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
    new_code = next_code([l[1] for l in links])
    url = input(f"Введите длинную ссылку для {new_code}{EXT}: ").strip()
    fname = new_code + EXT
    with open(fname, "w", encoding="utf-8") as f:
        f.write(make_html(url))
    print(f"Создано: {fname} → {url}")

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

    old_code, old_fname, old_url = links[idx]
    print(f"Текущий код: {old_code}, ссылка: {old_url}")
    # Новое имя файла
    codes_in_use = set(l[0] for l in links if l[0] != old_code)
    new_code = input_code(f"Новый код (Enter — не менять): ", used=codes_in_use) or old_code
    # Новая длинная ссылка
    new_url = input(f"Новая длинная ссылка (Enter — не менять): ").strip() or old_url

    # Проверить, надо ли переименовывать файл
    new_fname = new_code + EXT
    # Записать новый файл
    with open(new_fname, "w", encoding="utf-8") as f:
        f.write(make_html(new_url))
    # Удалить старый файл, если имя изменилось
    if new_fname != old_fname:
        try:
            os.remove(old_fname)
        except Exception:
            print("Не удалось удалить старый файл (возможно, уже удалён).")
    print(f"Ссылка обновлена: {new_fname} → {new_url}")

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
            print("Выход.")
            break
        else:
            print("Некорректный ввод.")

if __name__ == "__main__":
    main()
