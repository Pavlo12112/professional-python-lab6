from student_app.notifiers import ConsoleNotifier


def test_console_notifier_prints_recipient_and_message(capsys):
    ConsoleNotifier().send("Anna Koval", "Registered in group PI-21")

    output = capsys.readouterr().out

    assert output == "[notify -> Anna Koval] Registered in group PI-21\n"
