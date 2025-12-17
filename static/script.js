document.addEventListener("DOMContentLoaded", function () {
    const tipoRescisaoSelect = document.getElementById("tipo_rescisao");
    const avisoPedidoDemissaoDiv = document.getElementById("aviso_pedido_demissao");
    const dataFimDiv = document.getElementById("data_fim_div");
    const dataFimInput = document.querySelector('input[name="data_fim"]');
    const dataSolicitacaoInput = document.getElementById("data_solicitacao_demissao");
    const dataSaidaPretendidaInput = document.getElementById("data_saida_pretendida_div");
    const cumpriraAvisoRadios = document.querySelectorAll('input[name="cumprira_aviso"]');
    const feriasVencidasDiv = document.getElementById("ferias_vencidas_div");
    const dataInicioInput = document.querySelector('input[name="data_inicio"]');

    function toggleAvisoDemissao() {
        if (tipoRescisaoSelect.value === "pedido_demissao") {
            avisoPedidoDemissaoDiv.style.display = "block";
            dataFimDiv.style.display = "none";
            dataFimInput.required = false;
            dataSolicitacaoInput.required = true;
        } else {
            avisoPedidoDemissaoDiv.style.display = "none";
            dataFimDiv.style.display = "block";
            dataFimInput.required = true;
            dataSolicitacaoInput.required = false;
        }
    }

    function toggleDataSaida() {
        let selectedValue;
        for (const radio of cumpriraAvisoRadios) {
            if (radio.checked) {
                selectedValue = radio.value;
                break;
            }
        }

        if (selectedValue === "nao") {
            dataSaidaPretendidaInput.style.display = "block";
        } else {
            dataSaidaPretendidaInput.style.display = "none";
        }
    }

    function toggleFeriasVencidas() {
        const dataInicio = new Date(dataInicioInput.value);
        let dataFim;

        if (tipoRescisaoSelect.value === "pedido_demissao") {
            dataFim = new Date(dataSolicitacaoInput.value);
        } else {
            dataFim = new Date(dataFimInput.value);
        }

        if (dataInicio && dataFim && !isNaN(dataInicio) && !isNaN(dataFim)) {
            const diffTime = Math.abs(dataFim - dataInicio);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            feriasVencidasDiv.style.display = diffDays > 365 ? "block" : "none";
        } else {
            feriasVencidasDiv.style.display = "none";
        }
    }

    tipoRescisaoSelect.addEventListener("change", toggleAvisoDemissao);
    tipoRescisaoSelect.addEventListener("change", toggleFeriasVencidas);
    cumpriraAvisoRadios.forEach(radio => radio.addEventListener("change", toggleDataSaida));
    [dataInicioInput, dataFimInput, dataSolicitacaoInput].forEach(input => input.addEventListener("change", toggleFeriasVencidas));

    toggleAvisoDemissao();
    toggleDataSaida();
    toggleFeriasVencidas();
});
