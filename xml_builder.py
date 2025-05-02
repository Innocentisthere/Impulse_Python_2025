import xml.etree.ElementTree as ET
from xml.dom import minidom
import json


class XmlBuilder:
    def __init__(self, input_file: str):
        self.input_xml = ET.parse(input_file)
        self.root = self.input_xml.getroot()
        self.classes = self.root.findall("Class")
        self.aggregations = self.root.findall("Aggregation")
        self.new_root = None

    def find_root_class(self) -> ET.Element | None:
        """Находит корневой класс по атрибуту isRoot="true" """
        for cls in self.classes:
            if cls.attrib.get("isRoot", "").lower() == "true":
                return cls
        return None

    def get_element_attributes(self, element: ET.Element) -> list[ET.Element]:
        """Возвращает все атрибуты элемента"""
        return element.findall("Attribute")

    def find_class_by_name(self, name: str) -> ET.Element | None:
        """Находит класс по имени"""
        for cls in self.classes:
            if cls.attrib.get("name") == name:
                return cls
        return None

    def create_element_with_attributes(self, element: ET.Element) -> ET.Element:
        """Создает новый элемент с атрибутами"""
        new_element = ET.Element(element.attrib.get("name"))
        new_element.text = " "
        for attr in self.get_element_attributes(element):
            attr_name = attr.attrib.get("name")
            attr_type = attr.attrib.get("type")
            attr_el = ET.SubElement(new_element, attr_name)
            attr_el.text = attr_type

        return new_element

    def process_aggregations(self):
        """Обрабатывает все агрегации и строит структуру XML"""
        root_class = self.find_root_class()

        self.new_root = self.create_element_with_attributes(root_class)

        for agg in self.aggregations:
            source_name = agg.attrib.get("source")
            target_name = agg.attrib.get("target")
            source_class = self.find_class_by_name(source_name)
            new_el = self.create_element_with_attributes(source_class)

            if target_name == self.new_root.tag:
                self.new_root.append(new_el)
            else:
                target_elements = self.new_root.findall(target_name)
                if target_elements:
                    target_elements[0].append(new_el)

    def prettify_xml(self, element: ET.Element) -> str:
        """Форматирует XML с отступами"""
        rough_string = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        return '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    def build(self, output_file: str):
        """Основной метод для построения и сохранения XML"""
        self.process_aggregations()

        pretty_xml = self.prettify_xml(self.new_root)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

    def build_meta_json(self):
        meta = []
        root_class_name = self.find_root_class().attrib.get("name")


        for agg in self.aggregations:
            new_dict = dict()
            source_name = agg.attrib.get("source")
            target_name = agg.attrib.get("target")
            source_class = self.find_class_by_name(source_name)

            inner_attrs = source_class.attrib | agg.attrib
            for key, value in inner_attrs.items():
                if key == "name":
                    new_dict["class"] = value
                elif key in ["source", "target", "targetMultiplicity"]:
                    continue
                elif key == "sourceMultiplicity":
                    if value == "1":
                        new_dict["max"] = 1
                        new_dict["min"] = 1
                    else:
                        min, max = value.split("..")
                        new_dict["max"] = max
                        new_dict["min"] = min
                else:
                    new_dict[key] = value

            
            
            print(new_dict)



if __name__ == "__main__":
    builder = XmlBuilder("input/impulse_test_input.xml")
    builder.build_meta_json()
