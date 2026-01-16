<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";
    $reg_no = trim($_POST["reg_number"]);
    $defalt_passwd=password_hash("123@abc", PASSWORD_DEFAULT);
    $sql = "update users set passwd='$defalt_passwd' where userName='$reg_no';";
    $conn->query($sql);
    header("Location: ../dashbords/manageUsers.php?passwd_reset=true");
    exit();
