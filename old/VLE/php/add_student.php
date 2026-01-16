<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";

    $name=trim($_POST['name']);
    $email=trim($_POST['email']);
    $reg_no=trim($_POST['reg_number']);
    $faculty=trim($_POST['faculty']);
    $default_passwd=password_hash("123@abc", PASSWORD_DEFAULT);
    $role="student";
    $state="active";

    $sql_get_ids="select userName from users;";
    $result_ids=$conn->query($sql_get_ids);
    while($row_ids=$result_ids->fetch_array()){
        if($row_ids["userName"] ==$reg_no){
            header("Location:../dashbords/manageUsers.php?userNameerror=alredy_exsists");
            exit;
        }
    }

    $insertstudentinfo="
        insert into students(Registration_number,full_name,faculty,email) values (?,?,?,?);                                 
    ";
    $insertuserinfo="
        insert into users(userName,passwd,role,status) values (?,?,?,?);
    ";

    $stmnt=$conn->prepare($insertstudentinfo);
    $stmnt->bind_param("ssss",$reg_no,$name,$faculty,$email);
    $stmnt->execute();
    $stmnt->close();

    $user_stmt=$conn->prepare($insertuserinfo);
    $user_stmt->bind_param("ssss",$reg_no,$default_passwd,$role,$state);
    $user_stmt->execute();
    $user_stmt->close();

    header("Location:../dashbords/manageUsers.php?state=sucsess");
    exit;
?>