<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";

    $full_name = trim($_POST["name"]);
    $reg_no = trim($_POST["reg_number"]);
    $email = trim($_POST["email"]);
    $faculty = trim($_POST["faculty"]);
    $std_id = trim($_POST["id"]);
    $user_id = trim($_POST["user_id"]);

    $get_student_usernames = "select Registration_number from students where std_id!='$std_id';";
    $usernames=[];
    $users=$conn->query($get_student_usernames);
    while($row = $users->fetch_assoc()){
        array_push($usernames, $row["Registration_number"]);
    }
    foreach($usernames as $username){
        if($username == $reg_no){
            header("Location: ../dashbords/manageUsers.php?upadate_error=user_exsists");
            exit();
        }
    }


    $update_student_sql="
        update students set 
        full_name=?, Registration_number=?, faculty=?, email=?
        where std_id=?;
    ";

    $update_user_sql="
        update users set
        userName=?
        where id=?; 
    ";

    $stmnt=$conn->prepare($update_student_sql);
    $stmnt->bind_param("ssssi",$full_name,$reg_no,$faculty,$email,$std_id);
    $stmnt->execute();
    if($stmnt->affected_rows>0){
        $stmnt->close();
        $user_stmnt = $conn->prepare($update_user_sql);
        $user_stmnt->bind_param("si",$reg_no,$user_id);
        $user_stmnt->execute();
        if($user_stmnt->affected_rows> 0){
            $user_stmnt->close();
            header("Location: ../dashbords/manageUsers.php?upadate_status=successful");
            exit();
        }else{
            $user_stmnt->close();
            header("Location: ../dashbords/manageUsers.php?upadate_status=falier");
            exit();
        }
    }else{
        $stmnt->close();
        header("Location: ../dashbords/manageUsers.php?upadate_status=unsuccessful");
        exit();
    }
    
