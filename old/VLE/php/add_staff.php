<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";

    $staff_id=$name=$role=$email=$default_passwd="";

    $staff_id=trim($_POST['id']);
    $name=trim($_POST['name']);
    $role=trim($_POST['role']);
    $email=trim($_POST['email']);
    $default_passwd=password_hash("123@abc", PASSWORD_DEFAULT);
    $role="staff";
    $state="active";

    $stff="
        insert into staff(staff_id,full_name,email,sub_role) values (?,?,?,?);
    ";

    $stmnt=$conn->prepare($stff);
    $stmnt->bind_param("ssss", $staff_id,$name,$email,$role);
    $stmnt->execute();
    if($stmnt->affected_rows <1){
        header("Location: ../dashbords/manageUsers.php?insert_status=FAILED_stf");
        exit;
    }
    $stmnt->close();

    $user="
        insert into users(userName,passwd,role,status) values(?,?,?,?);
    ";
    $stmnt=$conn->prepare($user);
    $stmnt->bind_param("ssss", $staff_id,$default_passwd,$role,$state);
    $stmnt->execute();
    if($stmnt->affected_rows <1){
        header("Location: ../dashbords/manageUsers.php?insert_status=FAILED_usr");
        exit;
    }

    header("Location: ../dashbords/manageUsers.php?insert_status=true");
    exit;


