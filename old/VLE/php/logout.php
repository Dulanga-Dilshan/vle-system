<?php
session_start();
if(isset($_SESSION["role"])){
    include "config.php";
    $user=$_SESSION["username"];
    unset($_SESSION["username"]);
    unset($_SESSION["role"]);
    $sql="update users set active='no' where userName=?;";
    session_destroy();
    $stmnt=$conn->prepare($sql);
    $stmnt->bind_param("s",$user);
    $stmnt->execute();
    if($stmnt->affected_rows>0){
        header("Location:../index.php");
        exit;
    }
    header("Location:../index.php?error=logout_failed");
    exit;
}

