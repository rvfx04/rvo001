import streamlit as st

def login(users):
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        if (username, password) in users:
            st.success("Inicio de sesión exitoso para el usuario: {}".format(username))
        else:
            st.error("Usuario o contraseña incorrectos.")

def main():
    users = st.text_area("Ingrese la lista de usuarios y contraseñas en el formato 'usuario:contraseña', uno por línea:")
    users = [tuple(user.split(":")) for user in users.split("\n")]

    st.subheader("Inicio de Sesión")
    login(users)

if __name__ == "__main__":
    main()
