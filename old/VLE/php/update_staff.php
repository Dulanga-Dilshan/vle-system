<?php
    session_start();
    if(!isset($_SESSION["role"]) || $_SESSION["role"] != "admin") {
        header("Location: ../index.php");
        exit;
    }
    include "../php/config.php";

    $staff_id=trim($_POST["staff_id"]);
    $name=trim($_POST["name"]);
    $role=trim($_POST["role"]);
    $email=trim($_POST["email"]);
    $sid=trim($_POST["id"]);

    $user_id=trim($_POST["user_id"]);

    $ids=[];
    $stf_ids=$conn->query("select staff_id from staff where staff_id!='$staff_id';");
    while($row = $stf_ids->fetch_assoc()){
        array_push($ids,$row["staff_id"]);
    }
    foreach($ids as $id){
        if($id == $staff_id){
            header("Location: ../dashbords/manageUsers.php?update_status=member_already_exsists");
            exit;
        }
    }

    $update_sql="
        update staff set 
        full_name=?, staff_id=?, email=?, sub_role=?
        where id=?;
    ";
    $stmnt= $conn->prepare($update_sql);
    $stmnt->bind_param("ssssi", $name,$staff_id,$email,$role, $sid);
    $stmnt->execute();
    if($stmnt->affected_rows< 1){
        header("Location: ../dashbords/manageUsers.php?update_status=unsuccessful_$sid");
        exit;
    }
    $stmnt->close();
    $update_sql="
        update users set
        userName=?
        where ID=?
        ;
    ";
    $stmnt= $conn->prepare($update_sql);
    $stmnt->bind_param("si",$staff_id, $user_id);
    $stmnt->execute();
    if($stmnt->affected_rows< 1){
        header("Location: ../dashbords/manageUsers.php?update_status=FAILD$user_id");
        exit;
    }
    $stmnt->close();
    header("Location: ../dashbords/manageUsers.php?update_status=successful");
    exit;


