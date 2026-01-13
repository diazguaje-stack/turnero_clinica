const form = document.getElementById("formulario");

form.addEventListener("submit", function(e) {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value;
  const documento = document.getElementById("documento").value;

  fetch("/guardar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      nombre: nombre,
      documento: documento
    })
  })
   .then(res => res.json())
    .then(data => {
        if (data.ok) {
            alert("Turno registrado");
            document.getElementById("formulario").reset();
        }

    Swal.fire({
    title: "Turno asignado",
    text: "Su número es: " + data.codigo,
    icon: "success"
});

  });
});
