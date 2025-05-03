import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-response-ratings-widget',
  templateUrl: './response-ratings-widget.component.html',
  styleUrls: ['./response-ratings-widget.component.css']
})
export class ResponseRatingsWidgetComponent implements OnInit {
  ratings: number[] = [];

  constructor() {}

  ngOnInit(): void {
    // TODO: Call service to load chatbot ratings here
  }
}
