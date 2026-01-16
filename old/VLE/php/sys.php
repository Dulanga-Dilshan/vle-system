<?php

include "config.php";
function check_users(){
        global $conn;
        $date=date('Y-m-d');
        $sql = "update users set active='no' where last_login<?";
        $result = $conn->prepare($sql);
        $result->bind_param("s", $date);
        $result->execute();
        $result->close();
    }

    function is_active($username){
        global $conn;
        $sql="select active from users where userName='$username';";
        $result = $conn->query($sql);
        if($result->num_rows > 0){
            while($row = $result->fetch_assoc()){
                if($row["active"] == 'yes'){
                    return true;
                }
                return false;
            }
        }
    }