document.getElementById("contactForm")
.addEventListener("submit", function(e){
  e.preventDefault();
  document.getElementById("mensaje")
  .innerText = "Consulta enviada correctamente (modo demo).";
});
