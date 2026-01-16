<?php
session_start();
include "config.php";
$current_passwd=trim($_POST['current']);
$first_passwd=trim($_POST['first']);
$second_passwd=trim($_POST['second']);


if($first_passwd != $second_passwd){
    header('Location: ../dashbords/reset_passwd.php?pw_reset_error=new_passwd_not_match');
    exit;
}
if($current_passwd == $first_passwd){
    header('Location: ../dashbords/reset_passwd.php?pw_reset_error=use_a_new_passwd');
    exit;
}

$sql="select passwd from users where userName=?;";
$stmnt=$conn->prepare($sql);
$stmnt->bind_param("s",$_SESSION["username"]);
$stmnt->execute();
$result=$stmnt->get_result();
$row=$result->fetch_assoc();
if(password_verify($current_passwd,$row["passwd"])){
    $new_passwd_sql="update users set passwd=? where userName=?;";
    $new_passwd_result=$conn->prepare($new_passwd_sql);
    $new_passwd=password_hash($first_passwd,PASSWORD_DEFAULT);
    $new_passwd_result->bind_param("ss",$new_passwd,$_SESSION['username']);
    $new_passwd_result->execute();
    if($new_passwd_result->affected_rows> 0){
        header('Location: ../dashbords/passwd_state.html');
        exit;
    }
}else{
    header('Location: ../dashbords/reset_passwd.php?pw_reset_error=wrong_passwd');
    exit;
}
