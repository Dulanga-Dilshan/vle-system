<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";
    $reg_no = trim($_POST["reg_number"]);
    $sql = "update users set status='active' where userName='$reg_no';";
    $conn->query($sql);
    header("Location: ../dashbords/manageUsers.php");
    exit();