<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";
    $reg_no = trim($_POST["reg_number"]);
    $rm_user="delete from users where userName='$reg_no';";
    $rm_staff= "delete from staff where staff_id='$reg_no';";
    $conn->query($rm_user);
    $conn->query($rm_staff);
    header("Location: ../dashbords/manageUsers.php");
    exit();