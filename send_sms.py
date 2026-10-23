def send(phone: str, mesagge: str) -> bool:
    try:
        import pywhatkit as kit

        kit.sendwhatmsg_instantly(phone, mesagge)
        print("Mensaje enviado con exito")
        return True
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return False
