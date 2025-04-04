import { Component } from '@angular/core';

@Component({
  selector: 'chat-widget',
  templateUrl: './chat-widget.widget.html',
  styleUrls: ['./chat-widget.widget.css']
})
export class ChatWidget {
  isChatOpen = false;
  userMessage = '';
  messages: { id: number; text: string; sender: 'user' | 'bot' }[] = [
    { id: 1, text: "Hi! I'm ChadGPT. How can I help you today?", sender: 'bot' }
  ];
  private messageId = 2;

  toggleChat(): void {
    this.isChatOpen = !this.isChatOpen;
  }

  sendMessage(): void {
    const trimmed = this.userMessage.trim();
    if (!trimmed) return;

    this.messages.push({
      id: this.messageId++,
      text: trimmed,
      sender: 'user'
    });

    this.userMessage = '';

    setTimeout(() => {
      this.messages.push({
        id: this.messageId++,
        text: "I'm just a demo, but that's a great question!",
        sender: 'bot'
      });
    }, 600);
  }
}
