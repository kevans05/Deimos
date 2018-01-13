function myFunction() {
    var str=document.getElementById('editStaff').value.split(";");
    document.getElementById("id").value = str[0];
    document.getElementById("inputid").value = str[0];
    document.getElementById("inputFirstName").value = str[1];
    document.getElementById("inputLastName").value = str[2];
    document.getElementById("inputEmail").value = str[3];
    document.getElementById("inputPhoneNumber").value = str[4];
    document.getElementById("inputActive").value = str[5];
    document.getElementById("inputCorpID").value = str[6];

}