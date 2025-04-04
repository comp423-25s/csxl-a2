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

    let botReply = "I don't understand. Can you please rephrase?";

    const lower = trimmed.toLowerCase();
    if (lower.includes('update')) {
      botReply = 'Updated reservation to 2:00pm.';
    } else if (lower.includes('cancel')) {
      botReply = 'Reservation cancelled.';
    } else if (lower.includes('reserve')) {
      botReply = 'I have reserved you SN137 at 1:00pm.';
    } else if (lower.includes('thank')) {
      botReply = 'You are welcome!';
    } else if (lower.includes('chad')) {
      botReply = 'Chad is the best!';
    }
    setTimeout(() => {
      this.messages.push({
        id: this.messageId++,
        text: botReply,
        sender: 'bot'
      });
    }, 600);
  }
}
