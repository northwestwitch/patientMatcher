#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import pymongo
from pymongo.errors import ConnectionFailure
from flask.cli import FlaskGroup, with_appcontext, current_app
from flask_mail import Message
from patientMatcher import create_app
from .add import add
from .remove import remove

cli = FlaskGroup(create_app=create_app)

@click.group()
def test():
    """Test server using CLI"""
    pass

@cli.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)
    return current_app.name

@cli.command()
@with_appcontext
def connection():
    """Tests if Mongo client is connected"""
    try:
        current_app.client.admin.command('ismaster')
        click.echo('Connect test OK: Mongo client is connected')
    except ConnectionFailure:
        click.echo("Error: Mongo client is NOT connected!")
    except Exception as err:
        click.echo("Just testing the function")


@cli.command()
@with_appcontext
@click.option('-recipient', type=click.STRING, nargs=1, required=True, help="Email address to send the test email to")
def email(recipient):
    """Sends a test email using config settings"""
    click.echo(recipient)

    subj = 'Test email from patientMatcher'
    body = """
        ***This is an automated message, please do not reply to this email.***<br><br>
        If you receive this email it means that email settings are working fine and the
        server will be able to send match notifications.<br>
        A mail notification will be sent when:<br>
        <ul>
            <li>A patient is added to the database and the add request triggers a search
            on external nodes producing at least one result (/patient/add endpoint).</li>

            <li>An external search is actively performed on connected nodes and returns
            at least one result (/match/external/<patient_id> endpoint).</li>

            <li>The server is interrogated by an external node and returns at least one
            result match (/match endpoint). In this case a match notification is sent to
             each contact of the result matches.</li>

            <li>An internal search is submitted to the server using a patient from the
            database (/match endpoint) and this search returns at least one match.
            In this case contact users of all patients involved will be notified
            (contact from query patient and contacts from the result patients).</li>
        </ul>
        <br>
        You can stop server notification any time by commenting the MAIL_SERVER parameter in
        config file and rebooting the server.
        <br><br>
        Kind regards,<br>
        The PatienMatcher team
    """
    kwargs = dict(subject=subj, html=body, sender=current_app.config.get('MAIL_USERNAME'), recipients=[recipient])
    message = Message(**kwargs)
    try:
        current_app.mail.send(message)
        click.echo('Mail correctly sent. Check your inbox!')
    except Exception as err:
        click.echo('An error occurred while sending test email: "{}"'.format(err))

test.add_command(name)
test.add_command(connection)
test.add_command(email)
cli.add_command(test)
cli.add_command(add)
cli.add_command(remove)
