from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from gigapoll.button import CallbackButton
from gigapoll.data.models import Button
from gigapoll.data.models import Poll
from gigapoll.data.models import Template


def create_template(
        user_id: int,
        template_name: str,
        description: str,
        mode: str,
        session: Session,
        version: int = 1,
) -> Template:
    template = session.query(Template).where(
            Template.user_id == user_id,
            Template.name == template_name,
        ).one_or_none()

    if template:
        stmt = delete(Button).where(
                Button.template_id == template.id,
            )
        session.delete(template)
        session.execute(stmt)
        session.commit()

    template = Template(
            user_id=user_id,
            name=template_name,
            version=version,
            description=description,
            mode=mode
        )
    session.add(template)
    session.commit()
    return template


def get_template_by_name(
        user_id: int,
        template_name: str,
        session: Session,
) -> Template:
    return session.query(Template).where(
            Template.user_id == user_id,
            Template.name == template_name,
        ).one()


def get_buttons_for_empty_poll(
        template_id: int,
        session: Session,
) -> list[CallbackButton]:
    query_result = (
            session.query(
                Template.name,
                Button.value,
                Button.id,
            )
            .where(
                Template.id == template_id,
            )
            .join(Button, Template.id == Button.template_id)
            .all()
        )

    result = []
    for row in query_result:
        _, choice_name, id = row
        result.append(
                CallbackButton(
                    button_name=choice_name,
                    button_id=id,
                    votes=0,
                )
            )
    return result


def get_template_by_poll_id(
        poll_id: int,
        session: Session,
) -> Template:
    stmt = (
            select(Template)
            .join(
                Poll,
                and_(
                    Poll.id == poll_id,
                )
            )
            .where(
                Poll.id == poll_id,
            )
        )
    return session.scalars(stmt).one()


def get_template_by_cbdata(
        chat_id: int,
        message_id: int,
        session: Session,
) -> Template:
    stmt = (
            select(Template)
            .join(
                Poll,
                and_(
                    Poll.template_name == Template.name,
                    Poll.owner_id == Template.user_id,
                )
            )
            .where(
                Poll.chat_id == chat_id,
                Poll.message_id == message_id,
            )
        )
    return session.scalars(stmt).one()
