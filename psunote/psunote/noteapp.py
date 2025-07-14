import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/new", methods=["GET", "POST"])
@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def notes_save(note_id=None):
    db = models.db
    note = db.session.get(models.Note, note_id) if note_id else models.Note()

    form = forms.NoteForm(obj=note if note_id else None)

    if form.validate_on_submit():
        form.populate_obj(note)          # tags ถูกจัดการใน populate_obj ของฟิลด์แล้ว
        if not note_id:
            db.session.add(note)
        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template(
        "notes-create.html",
        form=form,
        note=note,
        is_edit=bool(note_id),
    )




@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )

@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def notes_delete(note_id):
    db = models.db
    note = db.session.get(models.Note, note_id)
    if not note:
        flask.abort(404)

    db.session.delete(note)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
