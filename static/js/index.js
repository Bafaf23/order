const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const fileName = document.getElementById("fileName");
const uploadIcon = document.getElementById("uploadIcon");
const uploadInstructions = document.getElementById("uploadInstructions");
const btnResetFile = document.getElementById("btnResetFile");
const btnSubmit = document.getElementById("btnSubmit");

// Detecta el cambio en el input (cuando seleccionan algo de forma puramente local)
fileInput.addEventListener("change", function () {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];

    fileName.textContent = file.name;
    uploadInstructions.innerHTML = `<span class="text-xs text-slate-400">Tamaño: ${(file.size / 1024).toFixed(1)} KB</span>`;

    uploadIcon.innerHTML =
      '<i class="fa-solid fa-file-circle-check text-orange-500"></i>';
    dropzone.classList.replace("border-slate-400", "border-orange-500");
    dropzone.classList.replace("bg-slate-100", "bg-orange-50");
    btnResetFile.classList.remove("hidden");

    btnSubmit.disabled = false;
    btnSubmit.classList.replace("bg-slate-300", "bg-orange-500");
    btnSubmit.classList.replace("text-slate-500", "text-white");
    btnSubmit.classList.replace("cursor-not-allowed", "hover:bg-orange-600");
  }
});

btnResetFile.addEventListener("click", function (e) {
  e.stopPropagation();
  fileInput.value = "";

  fileName.textContent = "No hay información para procesar";
  uploadInstructions.innerHTML =
    'Arrastra aquí tu archivo <span class="font-bold text-slate-600">.xlsx</span> o <span class="font-bold text-slate-600">.csv</span> (o haz clic)';

  uploadIcon.innerHTML = '<i class="fa-solid fa-file-arrow-up"></i>';
  dropzone.classList.replace("border-orange-500", "border-slate-400");
  dropzone.classList.replace("bg-orange-50", "bg-slate-100");
  btnResetFile.classList.add("hidden");

  btnSubmit.disabled = true;
  btnSubmit.classList.replace("bg-orange-500", "bg-slate-300");
  btnSubmit.classList.replace("text-white", "text-slate-500");
  btnSubmit.classList.replace("hover:bg-orange-600", "cursor-not-allowed");
});

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(
    eventName,
    (e) => {
      e.preventDefault();
      dropzone.classList.add("border-orange-500", "bg-orange-50");
    },
    false,
  );
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(
    eventName,
    (e) => {
      e.preventDefault();
      if (fileInput.files.length === 0) {
        dropzone.classList.remove("border-orange-500", "bg-orange-50");
      }
    },
    false,
  );
});

dropzone.addEventListener(
  "drop",
  (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;

      fileInput.dispatchEvent(new Event("change"));
    }
  },
  false,
);
