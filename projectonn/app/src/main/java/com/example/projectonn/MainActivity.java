package com.example.projectonn;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Button toepic = findViewById(R.id.intent_epic);
                toepic.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Intent intent = new Intent(MainActivity.this, epic_entry.class);
                startActivity(intent);
            }
        });
    }
    @Override
    public void onBackPressed(){
        super.onBackPressed();
    }
}