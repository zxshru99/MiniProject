package com.agripredict;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class AgriPredictApplication {

    public static void main(String[] args) {
        SpringApplication.run(AgriPredictApplication.class, args);
    }
}
