/* =========================================================== */
/* 🟪 ARIONEDEV – JS EXCLUSIVO DA TELA EMPRESA                 */
/* =========================================================== */

/* ----------------------------- */
/* 🔽 Dropdown de ações          */
/* ----------------------------- */
document.addEventListener("DOMContentLoaded", () => {
    const btnAcoes = document.querySelector(".btn-acoes");
    const menuAcoes = document.querySelector(".acoes-menu");

    if (btnAcoes && menuAcoes) {
        btnAcoes.addEventListener("click", () => {
            menuAcoes.style.display =
                menuAcoes.style.display === "block" ? "none" : "block";
        });

        document.addEventListener("click", (e) => {
            if (!e.target.closest(".empresa-acoes")) {
                menuAcoes.style.display = "none";
            }
        });
    }
});


/* ----------------------------- */
/* 🖼️ Preview da Logo            */
/* ----------------------------- */
const inputLogo = document.getElementById("inputLogo");
const previewLogo = document.getElementById("previewLogo");
const logoAtual = document.getElementById("logoAtual");

if (inputLogo) {
    inputLogo.addEventListener("change", (e) => {
        const arquivo = e.target.files[0];

        if (!arquivo) {
            previewLogo.style.display = "none";
            logoAtual.style.display = "block";
            return;
        }

        if (arquivo.type !== "image/png") {
            alert("⚠️ Apenas arquivos PNG são permitidos.");
            inputLogo.value = "";
            return;
        }

        const leitor = new FileReader();
        leitor.onload = (ev) => {
            logoAtual.style.display = "none";
            previewLogo.style.display = "block";
            previewLogo.src = ev.target.result;
        };
        leitor.readAsDataURL(arquivo);
    });
}


/* ----------------------------- */
/* 📅 Máscara Data               */
/* ----------------------------- */
function mascaraData(valor) {
    valor = valor.replace(/\D/g, "").slice(0, 8);
    if (valor.length >= 5)
        return valor.replace(/(\d{2})(\d{2})(\d{4})/, "$1/$2/$3");
    if (valor.length >= 3)
        return valor.replace(/(\d{2})(\d{2})/, "$1/$2");
    return valor;
}

document.querySelectorAll("input[name='data_abertura']").forEach((campo) => {
    campo.addEventListener("input", (e) => {
        e.target.value = mascaraData(e.target.value);
    });
});
