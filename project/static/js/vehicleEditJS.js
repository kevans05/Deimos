function autoFillVehicle() {
    var str=document.getElementById('editVehicle').value.split(";");

    document.getElementById("id").value = str[0];
    document.getElementById("inputid").value = str[0];
    document.getElementById("inputNickname").value = str[2];
    document.getElementById("inputCorporationID").value = str[3];
    document.getElementById("inputMake").value = str[4];
    document.getElementById("inputModel").value = str[5];
    document.getElementById("inputActive").value = str[1];
}
