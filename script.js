document.getElementById('registerForm').addEventListener('submit', function(event){
    const birthDate = new Date(this.birth_date.value);
    const age = (new Date() - birthDate) / (1000*60*60*24*365);
    if(age < 18){
        alert("Debes ser mayor de 18 años");
        event.preventDefault();
        return;
    }

    const password = this.password.value;
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
    if(!pattern.test(password)){
        alert("La contraseña no cumple la política de seguridad");
        event.preventDefault();
        return;
    }
});
