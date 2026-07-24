const openBtn = document.getElementById("openModal");
const closeBtn = document.getElementById("closeModal");
const modal = document.getElementById("miModal");
const contenido = document.getElementById("modalContenido");

openBtn.addEventListener("click", () => {
  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");

  contenido.classList.remove("scale-95", "translate-y-4");
  contenido.classList.add("scale-100", "translate-y-0");
});

closeBtn.addEventListener("click", () => {
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");

  contenido.classList.remove("scale-100", "translate-y-0");
  contenido.classList.add("scale-95", "translate-y-4");
});
