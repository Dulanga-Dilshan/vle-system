<?php
    $usr= "vleSystem";
    $pass= "dehue7543FS";
    $host= "localhost";
    $db = "vle";


    $conn =new  mysqli($host, $usr, $pass, $db);
    if($conn->connect_error){
        die($conn->connect_error);
    }

