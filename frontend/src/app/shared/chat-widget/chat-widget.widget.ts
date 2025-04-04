import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'chat-widget',
  templateUrl: './chat-widget.widget.html',
  styleUrls: ['./chat-widget.widget.css']
})
export class ChatWidget {
  constructor(private router: Router) {}

  openChat(): void {
    this.router.navigate(['/chat']);
  }
}