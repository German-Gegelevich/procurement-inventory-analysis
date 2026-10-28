# Публикация на GitHub

Рекомендуемое имя: `procurement-inventory-analysis`. Описание: «SQL и Excel: планирование пополнения запасов на синтетических данных». Темы: sql, sqlite, excel, procurement, inventory-management, portfolio.

## Через браузер

1. Войдите в GitHub и создайте новый репозиторий с указанным именем.
2. Выберите Public для портфолио. Не загружайте исходные коммерческие файлы.
3. Распакуйте архив проекта на компьютере.
4. Выберите Add file → Upload files и перетащите содержимое папки проекта, сохранив вложенные папки.
5. Проверьте наличие README.md в корне и отображение картинки.
6. На странице профиля закрепите репозиторий и добавьте его ссылку в резюме.

## Через Git

Создайте пустой репозиторий без README, затем из папки проекта:

```bash
git init
git add .
git commit -m "Add procurement analytics portfolio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/procurement-inventory-analysis.git
git push -u origin main
```

Замените YOUR_USERNAME своим логином. Не помещайте пароли и токены в файлы. В проект не включена лицензия: при необходимости автор выбирает её отдельно. Файл Excel и CSV содержат только синтетические данные.
