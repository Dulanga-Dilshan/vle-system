<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";
    $reg_no = trim($_POST["reg_number"]);
    $rm_user="delete from users where userName='$reg_no';";
    $rm_student= "delete from students where Registration_number='$reg_no';";
    $conn->query($rm_user);
    $conn->query($rm_student);
    header("Location: ../dashbords/manageUsers.php");
    exit();