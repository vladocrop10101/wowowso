from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
import os
import io
from flask import jsonify, Blueprint, render_template, request, redirect, url_for, Response
# routes.py
from datetime import datetime
from models import StorageUnit, db, Warehouse

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def home():
    units = StorageUnit.query.all()
    return render_template('home.html', units=units)


@main_blueprint.route('/add-storage-unit', methods=['GET', 'POST'])
def add_storage_unit():
    if request.method == 'POST':
        try:
            # Чтение данных из формы
            unit_id = request.form.get('unit_id')
            full_name = request.form.get('full_name')
            phone = request.form.get('phone')
            car_number = request.form.get('car_number')
            car_model = request.form.get('car_model')
            tire_width = request.form.get('tire_width')
            tire_profile = request.form.get('tire_profile')
            tire_diameter = request.form.get('tire_diameter')
            tire_name = request.form.get('tire_name') or ''
            has_disks = request.form.get('has_disks') == 'on'  # Если галочка выбрана
            tire_quantity = request.form.get('tire_quantity') or 0
            storage_date = request.form.get('storage_date')  # Ожидается формат YYYY-MM-DD
            warehouse = 1
            warehouse_id = 1
            row = 1
            place = 1

            # Валидация обязательных полей
            missing_fields = []
            if not unit_id:
                missing_fields.append("unit_id")
            if not full_name:
                missing_fields.append("full_name")
            if not phone:
                missing_fields.append("phone")
            if not warehouse_id:
                missing_fields.append("warehouse_id")

            if missing_fields:
                return jsonify({"error": f"Обязательные поля не заполнены: {', '.join(missing_fields)}"}), 400

            # Проверка уникальности unit_id
            if StorageUnit.query.filter_by(unit_id=unit_id).first():
                return jsonify({"error": "unit_id уже существует"}), 400

            # Преобразование tire_quantity в число
            try:
                tire_quantity = int(tire_quantity)
            except ValueError:
                return jsonify({"error": "Количество шин должно быть числом"}), 400

            # Валидация и преобразование storage_date
            try:
                if storage_date:
                    storage_date = datetime.strptime(storage_date, '%Y-%m-%d').date()
                else:
                    storage_date = None
            except ValueError:
                return jsonify({"error": "Неверный формат даты. Ожидается YYYY-MM-DD"}), 400

            # Проверка существования склада
            warehouse = Warehouse.query.get(warehouse_id)
            if not warehouse:
                return jsonify({"error": "Склад с таким ID не найден"}), 400

            # Создание нового объекта StorageUnit
            new_unit = StorageUnit(
                unit_id=unit_id,
                full_name=full_name,
                phone=phone,
                car_number=car_number,
                car_model=car_model,
                tire_width=tire_width,
                tire_profile=tire_profile,
                tire_diameter=tire_diameter,
                tire_name=tire_name,
                has_disks=has_disks,
                tire_quantity=tire_quantity,
                storage_date=storage_date,
                warehouse_id=warehouse_id,  # Устанавливаем warehouse_id
                warehouse=warehouse,
                row=row,
                place=place
            )

            # Добавление в базу данных
            db.session.add(new_unit)
            db.session.commit()

            return redirect(url_for('main.home'))

        except Exception as e:
            # Обработка ошибок
            db.session.rollback()
            return jsonify({"error": "Ошибка сервера", "details": str(e)}), 500

    return render_template('add_storage_unit.html')


@main_blueprint.route('/edit-storage-unit/<int:unit_id>', methods=['POST'])
def edit_storage_unit(unit_id):
    # Знайти запис за unit_id
    unit = StorageUnit.query.get(unit_id)
    if not unit:
        return jsonify({"error": "Запис не знайдено"}), 404

    try:
        # Отримати дані з запиту
        data = request.json

        # Оновити поля
        unit.unit_id = data.get('unit_id', unit.unit_id)
        unit.full_name = data.get('full_name', unit.full_name)
        unit.phone = data.get('phone', unit.phone)
        unit.car_number = data.get('car_number', unit.car_number)
        unit.car_model = data.get('car_model', unit.car_model)
        unit.tire_width = data.get('tire_width', unit.tire_width)
        unit.tire_profile = data.get('tire_profile', unit.tire_profile)
        unit.tire_diameter = data.get('tire_diameter', unit.tire_diameter)
        unit.tire_name = data.get('tire_name', unit.tire_name)
        unit.has_disks = data.get('has_disks', unit.has_disks)
        unit.tire_quantity = data.get('tire_quantity', unit.tire_quantity)

        # Перетворити дату з тексту в об'єкт
        storage_date = data.get('storage_date')
        if storage_date:
            unit.storage_date = datetime.strptime(storage_date, '%Y-%m-%d').date()

        # Оновити інші параметри з location
        unit.warehouse = data.get('warehouse', unit.warehouse)
        unit.row = data.get('row', unit.row)
        unit.place = data.get('place', unit.place)

        # Зберегти зміни
        db.session.commit()

        return jsonify({"message": "Запис успішно оновлено"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Помилка оновлення даних", "details": str(e)}), 500


@main_blueprint.route('/delete-storage-unit/<int:unit_id>', methods=['POST'])
def delete_storage_unit(unit_id):
    unit = StorageUnit.query.get(unit_id)
    if unit:
        db.session.delete(unit)
        db.session.commit()
        return redirect(url_for('main.home'))

    return jsonify({"error": "Unit not found"}), 404


@main_blueprint.route('/summary')
def summary():
    units = StorageUnit.query.with_entities(
        StorageUnit.unit_id,
        StorageUnit.tire_width,
        StorageUnit.tire_profile,
        StorageUnit.tire_diameter,
        StorageUnit.tire_name,
        StorageUnit.has_disks,
        StorageUnit.tire_quantity,
        StorageUnit.warehouse,
        StorageUnit.row,
        StorageUnit.place
    ).all()

    return render_template('summary.html', units=units)


@main_blueprint.route('/update-summary/<int:unit_id>', methods=['POST'])
def update_summary(unit_id):
    unit = StorageUnit.query.get(unit_id)
    if not unit:
        return jsonify({"error": "Запис не знайдено."}), 404

    data = request.json

    unit.warehouse = data.get('warehouse', unit.warehouse)
    unit.row = data.get('row', unit.row)
    unit.place = data.get('place', unit.place)

    db.session.commit()

    return jsonify({"message": "Storage unit updated successfully"})


# знизу видалити
@main_blueprint.route('/api/storage-units')
def get_storage_units():
    units = StorageUnit.query.all()
    response = [
        {
            "id": unit.id,
            "row": unit.row,
            "place": unit.place,
            "status": "occupied" if unit.has_disks else "free",  # Приклад статусу
        }
        for unit in units
    ]
    return jsonify(response)


@main_blueprint.route('/api/storage-unit/<int:unit_id>', methods=['POST'])
def update_storage_unit(unit_id):
    data = request.json
    status = data.get("status")
    unit = StorageUnit.query.get(unit_id)

    if not unit:
        return jsonify({"error": "Storage unit not found"}), 404

    if status == "occupied":
        unit.is_occupied = True
    elif status == "free":
        unit.is_occupied = False
    elif status == "reserve":
        unit.is_reserved = True
    else:
        return jsonify({"error": "Invalid status"}), 400

    db.session.commit()
    return jsonify({"message": "Status updated successfully"})


@main_blueprint.route('/interactive-warehouse')
def interactive_warehouse():
    return render_template('visual.html')  # Ваш HTML-файл


# зверху видалити

@main_blueprint.route('/warehouses')
def get_warehouses():
    """Возвращает список складов."""
    warehouses = Warehouse.query.all()
    response = [
        {
            "id": warehouse.id,
            "name": warehouse.name,
            "rows": warehouse.rows,
            "columns": warehouse.columns,
            "layout": warehouse.layout,
        }
        for warehouse in warehouses
    ]
    return jsonify(response)


@main_blueprint.route('/warehouse/<int:warehouse_id>')
def get_warehouse(warehouse_id):
    """Возвращает данные конкретного склада."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({"error": "Склад не найден"}), 404
    return jsonify({
        "id": warehouse.id,
        "name": warehouse.name,
        "rows": warehouse.rows,
        "columns": warehouse.columns,
        "layout": warehouse.layout,
    })


@main_blueprint.route('/add-warehouse', methods=['POST'])
def add_warehouse():
    """Добавляет новый склад."""
    data = request.json
    name = data.get('name')
    rows = data.get('rows', 10)
    columns = data.get('columns', 10)
    layout = data.get('layout', [])

    if not name:
        return jsonify({"error": "Название склада обязательно"}), 400

    warehouse = Warehouse(name=name, rows=rows, columns=columns, layout=layout)
    db.session.add(warehouse)
    db.session.commit()

    return jsonify({"message": "Склад добавлен", "id": warehouse.id})


@main_blueprint.route('/update-warehouse/<int:warehouse_id>', methods=['POST'])
def update_warehouse(warehouse_id):
    """Обновляет данные склада."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({"error": "Склад не найден"}), 404

    data = request.json
    warehouse.name = data.get('name', warehouse.name)
    warehouse.rows = data.get('rows', warehouse.rows)
    warehouse.columns = data.get('columns', warehouse.columns)
    warehouse.layout = data.get('layout', warehouse.layout)

    db.session.commit()
    return jsonify({"message": "Склад обновлен"})


@main_blueprint.route('/delete-warehouse/<int:warehouse_id>', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Удаляет склад."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({"error": "Склад не найден"}), 404

    db.session.delete(warehouse)
    db.session.commit()
    return jsonify({"message": "Склад удален"})


# Подключаем шрифт с поддержкой кириллицы (замени путь на актуальный)
FONT_PATH = os.path.join(os.getcwd(), "static", "fonts", "Arialmt.ttf")
FONT_BOLD_PATH = os.path.join(os.getcwd(), "static", "fonts", "Arial_bolditalicmt.ttf")

pdfmetrics.registerFont(TTFont("Arial", FONT_PATH))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_BOLD_PATH))


@main_blueprint.route('/print-label/<int:unit_id>')
def print_label(unit_id):
    unit = StorageUnit.query.get(unit_id)
    if not unit:
        return jsonify({"error": "Запись не найдена"}), 404

    buffer = io.BytesIO()
    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    def draw_label(x, y):
        """Рисует одну этикетку в указанной позиции"""
        pdf.setFont("Arial-Bold", 250)  # Используем шрифт с кириллицей
        pdf.drawCentredString(x + page_width / 4, y + 100, str(unit.unit_id))

        pdf.setFont("Arial", 30)
        pdf.drawCentredString(x + page_width / 4, y + 60, f' {unit.full_name},  {unit.phone}' )
        pdf.drawCentredString(x + page_width / 4, y + 30,
                              f"Авто: {unit.car_number}, {unit.tire_width}/{unit.tire_profile}/{unit.tire_diameter}, {unit.tire_name}")
        pdf.drawCentredString(x + page_width / 4, y, f" Диски: {'Да' if unit.has_disks else 'Нет'}, {unit.tire_quantity}, {unit.storage_date}")

    offsets = [(0, page_height / 2), (page_width / 2, page_height / 2), (0, 0), (page_width / 2, 0)]
    for x, y in offsets:
        draw_label(x, y)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf',
                    headers={"Content-Disposition": f"inline; filename=label_{unit_id}.pdf"})
