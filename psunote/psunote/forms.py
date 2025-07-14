# forms.py
from flask_wtf import FlaskForm
from wtforms import Field, widgets
from wtforms_sqlalchemy.orm import model_form

import models   # โมเดลของคุณ

# ---------- ฟิลด์แท็กแบบคอมมา ----------
class TagListField(Field):
    """รับ/แสดงแท็กเป็นข้อความคั่นด้วยคอมมา เช่น  'dev, python'"""
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates

    # --- อ่านค่าจากฟอร์ม (POST) ---
    def process_formdata(self, valuelist):
        if valuelist:
            items = [x.strip() for x in valuelist[0].split(",") if x.strip()]
            if self.remove_duplicates:
                seen = set()
                self.data = [x for x in items if x not in seen and not seen.add(x)]
            else:
                self.data = items
        else:
            self.data = []

    # --- ใส่ค่าลงฟอร์ม (GET) ---
    def process_data(self, value):
        # value == note.tags (ลิสต์ Tag) หรือ None
        self.data = [t.name for t in value] if value else []

    # --- ตอน populate_obj ลงโมเดล ---
    def populate_obj(self, obj, name):
        db = models.db
        tag_objs = []
        for tag_name in self.data:
            tag = (
                db.session.execute(
                    db.select(models.Tag).where(models.Tag.name == tag_name)
                )
                .scalars()
                .first()
            )
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)
            tag_objs.append(tag)
        setattr(obj, name, tag_objs)

    def _value(self):
        return ", ".join(self.data) if self.data else ""

# ---------- ฟอร์มโน้ต ----------
# ตัด created/updated/tags ออก เพราะเราจะจัดการเอง
BaseNoteForm = model_form(
    models.Note,
    base_class=FlaskForm,
    exclude=["created_date", "updated_date", "tags"],
    db_session=models.db.session,
)

class NoteForm(BaseNoteForm):
    tags = TagListField("Tags")   # ฟิลด์แท็กที่เราสร้างเอง
