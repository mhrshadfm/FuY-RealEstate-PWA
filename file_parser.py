from typing import Dict, Any


class FileParser:

    def __init__(self):
        pass

    # -----------------------------
    # تبدیل لیست فیلدها به دیکشنری
    # -----------------------------
    def fields_to_dict(self, fields):

        result = {}

        for field in fields:

            key = field.get("fieldKey")

            if not key:
                key = field.get("fieldTitle")

            value = field.get("textValue")

            if value is None:
                value = field.get("value")

            result[key] = value

        return result

    # -----------------------------
    # استخراج مشخصات اصلی
    # -----------------------------
    def parse(self, data: Dict[str, Any]):

        result = {

            "id": data.get("id"),

            "serial": data.get("serial"),

            "fileCode": data.get("fileCode"),

            "fileDate": data.get("fileDateShamsi"),

            "updateDate": data.get("updateDate"),

            "propertyType": data.get("propertyTypeTitle"),

            "orderType": data.get("orderTypeTitle"),

            "district": data.get("districtZoneTitle"),

            "districtFull": data.get("districtZoneFullTitle"),

            "address": data.get("address"),

            "description": data.get("description"),

            "owner": data.get("ownerName"),

            "phone1": data.get("phone1"),

            "phone2": data.get("phone2"),

            "status": data.get("status"),

            "statusKey": data.get("statusKey"),

            "isAvailable": data.get("isAvailable"),

            "acceptColleague": data.get("acceptColleague"),

            "latitude": data.get("latitude"),

            "longitude": data.get("longitude")

        }

        result["price"] = {

            "priceTotal": data.get("priceTotal"),

            "pricePerMeter": data.get("pricePerMeter"),

            "deposit": data.get("rentPriceDeposit"),

            "rent": data.get("rentPrice")

        }

        result["generalFields"] = {}

        result["items"] = []

        return self.fill_fields(result, data)

    # -----------------------------
    # مشخصات عمومی ملک
    # -----------------------------
    def fill_fields(self, result, data):

        for field_set in data.get("fieldSets", []):

            title = field_set.get("fieldSetTitle")

            fields = self.fields_to_dict(

                field_set.get("fields", [])

            )

            if title is None:
                title = "عمومی"

            result["generalFields"][title] = fields

        for item in data.get("fileItems", []):

            result["items"].append(

                self.parse_item(item)

            )

        return result

    # -----------------------------
    # اطلاعات هر واحد
    # -----------------------------
    def parse_item(self, item):

        return {

            "fileItemId": item.get("fileItemId"),

            "propertyArea": item.get("propertyArea"),

            "priceTotal": item.get("priceTotal"),

            "pricePerMeter": item.get("pricePerMeter"),

            "deposit": item.get("rentPriceDeposit"),

            "rent": item.get("rentPrice"),

            "description": item.get("description"),

            "fields": self.fields_to_dict(

                item.get("fields", [])

            )

        }

    # -----------------------------
    # فقط شماره سریال
    # -----------------------------
    def serial(self, data):

        return data.get("serial")

    # -----------------------------
    # تاریخ شمسی
    # -----------------------------
    def shamsi_date(self, data):

        return data.get("fileDateShamsi")

    # -----------------------------
    # شماره تلفن
    # -----------------------------
    def phones(self, data):

        return [

            data.get("phone1"),

            data.get("phone2")

        ]

    # -----------------------------
    # قیمت
    # -----------------------------
    def prices(self, data):

        return {

            "deposit": data.get("rentPriceDeposit"),

            "rent": data.get("rentPrice"),

            "total": data.get("priceTotal"),

            "perMeter": data.get("pricePerMeter")

        }



