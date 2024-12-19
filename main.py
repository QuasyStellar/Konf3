import re
import xml.etree.ElementTree as ET


# Функция для вычисления выражений
def evaluate_expression(expr, variables):
    # Заменяем переменные на их значения в выражении
    for var_name, value in variables.items():
        expr = expr.replace(var_name, str(value))

    try:
        # Применяем eval() для вычисления выражений
        return eval(expr)
    except Exception as e:
        raise ValueError(f"Ошибка вычисления выражения '{expr}': {str(e)}")


# Функция для парсинга значений (числа, строки, массивы)
def parse_value(value):
    if value.startswith("[[") and value.endswith("]]"):
        # Это строка
        return value[2:-2]
    elif value.startswith("#(") and value.endswith(")"):
        # Это массив
        elements = value[2:-1].split(",")
        return [parse_value(el.strip()) for el in elements]
    elif re.match(r"^\d+$", value):
        # Это число
        return int(value)
    else:
        # Прочее (например, переменная)
        return value


# Функция для парсинга объявления переменной
def parse_var_declaration(line):
    match = re.match(r"var\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.*);", line)
    if match:
        var_name = match.group(1)
        value = parse_value(match.group(2))
        return var_name, value
    return None, None


# Функция для парсинга выражений с вычислениями
def parse_expression(line):
    # Убираем начальные и конечные символы |
    expr = line.strip("|")
    return expr


# Функция для преобразования в XML
def convert_to_xml(parsed_data):
    root = ET.Element("configuration")

    for var_name, value in parsed_data.items():
        var_element = ET.SubElement(root, "var", name=var_name)
        if isinstance(value, list):
            array_element = ET.SubElement(var_element, "array")
            for item in value:
                item_element = ET.SubElement(array_element, "item")
                item_element.text = str(item)
        else:
            var_element.text = str(value)

    tree = ET.ElementTree(root)
    tree.write("output.xml", encoding="utf-8", xml_declaration=True)


# Основная функция для обработки входных данных
def process_input():
    parsed_data = {}
    while True:
        try:
            line = input().strip()
            if not line:
                continue

            # Обработка объявления переменной
            if line.startswith("var"):
                var_name, value = parse_var_declaration(line)
                if var_name:
                    if "|" in str(value):
                        expr = parse_expression(value)
                        result = evaluate_expression(expr, parsed_data)
                        parsed_data[var_name] = result
                    else:
                        parsed_data[var_name] = value
                else:
                    print(f"Ошибка синтаксиса в объявлении переменной: {line}")

            # Обработка выражений (вычислений)
            elif "|" in line:
                expr = parse_expression(line)
                result = evaluate_expression(expr, parsed_data)

            else:
                print(f"Неподдерживаемая строка: {line}")

        except EOFError:
            break
        except ValueError as e:
            print(f"Ошибка: {e}")
            break

    convert_to_xml(parsed_data)
    print("Конвертация завершена. Выходной XML сохранен в 'output.xml'.")


# Запуск обработки
if __name__ == "__main__":
    process_input()
