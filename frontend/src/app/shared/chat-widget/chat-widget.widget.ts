import {
  AfterViewChecked,
  Component,
  ElementRef,
  ViewChild,
  OnInit
} from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface User {
  id: number;
  pid: number;
  onyen: string;
  first_name: string;
  last_name: string;
  email: string;
  pronouns: string;
  github: string;
  github_id?: number;
  github_avatar?: string;
  accepted_community_agreement: boolean;
  bio?: string;
  linkedin?: string;
  website?: string;
}

@Component({
  selector: 'chat-widget',
  templateUrl: './chat-widget.widget.html',
  styleUrls: ['./chat-widget.widget.css']
})
export class ChatWidget implements AfterViewChecked, OnInit {
  constructor(private http: HttpClient) {
    this.fetchUser();
  }
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  isChatOpen = false;
  userMessage = '';
  private messageId = 2;
  private shouldScroll = false;
  private justOpenedChat = false;
  ratings: { [messageId: number]: number } = {};
  stars = [1, 2, 3, 4, 5];
  userId: number | null = null;
  myCourses: any;
  selectedCourseSiteId: any;
  selectedTicketType: 'conceptual' | 'assignment' | '' = '';
  taTicket = {
    className: '',
    conceptualQuestion: '',
    assignmentSection: '',
    assignmentDescription: '',
    assignmentConcepts: '',
    assignmentAttempts: ''
  };

  messages: { id: number; text: string; sender: 'user' | 'bot'; time: Date }[] =
    [
      {
        id: 1,
        text: "Hi! I'm ChadGPT. How can I help you today?",
        sender: 'bot',
        time: new Date(Date.now())
      }
    ];

  submitTicketAsMessage(): void {
    let message = `TA Ticket Submission\n`;
    message += `Type: ${this.selectedTicketType}\n`;

    if (this.selectedTicketType === 'conceptual') {
      message += `Question: ${this.taTicket.conceptualQuestion}\n`;
    } else if (this.selectedTicketType === 'assignment') {
      message += `Section: ${this.taTicket.assignmentSection}\n`;
      message += `Description: ${this.taTicket.assignmentDescription}\n`;
      message += `Concepts: ${this.taTicket.assignmentConcepts}\n`;
      message += `Attempts: ${this.taTicket.assignmentAttempts}\n`;
    }

    const formatted = message.trim();

    this.userMessage = formatted;
    this.saveMessagesToLocalStorage();
    this.cancelTicketForm();
    this.scrollToBottom();
    this.sendMessage();
  }

  cancelTicketForm(): void {
    this.selectedTicketType = '';
    this.taTicket = {
      conceptualQuestion: '',
      assignmentSection: '',
      assignmentDescription: '',
      assignmentConcepts: '',
      assignmentAttempts: '',
      className: ''
    };
  }

  setRating(star: number, messageId: number): void {
    this.ratings[messageId] = star;
    localStorage.setItem('chatRatings', JSON.stringify(this.ratings));
  }

  isReservationConfirmation(message: string): boolean {
    const pattern = /^✅ Room .+ reserved from .+ to .+$/;
    return pattern.test(message);
  }
  isReservationChangeConfirmation(message: string): boolean {
    const pattern =
      /^Reservation .+ was cancelled\. New reservation created for room .+ from .+ to .+.$/;
    return pattern.test(message);
  }

  isReservationCancellationConfirmation(message: string): boolean {
    const pattern = /^ Reservation .+ has been cancelled\.$/;
    return pattern.test(message);
  }

  isOfficeHour(message: string): boolean {
    const pattern = /^Your office hour for .+$/;
    return pattern.test(message);
  }

  isOfficeHourConfirmed(message: string): boolean {
    const pattern = /^Ticket created for .+$/;
    return pattern.test(message);
  }

  fetchUser() {
    const token = localStorage.getItem('bearerToken');
    if (!token) return;

    this.http
      .get<User>('/api/user/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .subscribe({
        next: (user) => {
          this.userId = user.id;
        },
        error: (err) => {
          console.error('Unable to fetch user:', err);
        }
      });
  }

  toggleChat(): void {
    this.isChatOpen = !this.isChatOpen;
    if (this.isChatOpen) {
      this.shouldScroll = true;
      this.justOpenedChat = true;
    } else if (!this.isChatOpen) {
      this.sendConversationToDatabase();
    }
  }

  loadRatingsFromLocalStorage(): void {
    const stored = localStorage.getItem('chatRatings');
    if (stored) {
      this.ratings = JSON.parse(stored);
    }
  }

  ngOnInit(): void {
    this.loadMessagesFromLocalStorage();
    this.loadRatingsFromLocalStorage();
  }

  sendMessage(): void {
    const trimmed = this.userMessage.trim();
    if (!trimmed) return;

    // Add user's message to chat
    this.messages.push({
      id: this.messageId++,
      text: trimmed,
      sender: 'user',
      time: new Date(Date.now())
    });
    this.saveMessagesToLocalStorage();
    this.userMessage = '';
    this.shouldScroll = true;

    const recentMessages = this.messages.slice(-10);
    const openaiFormattedHistory = recentMessages.map((m) => ({
      role: m.sender === 'bot' ? 'assistant' : 'user',
      content: m.text
    }));

    const token = localStorage.getItem('bearerToken');

    // 🧠 Naive room ID extraction (replace with NLP later if needed)
    const roomIdMatch = trimmed.match(/room\s+(\w+)/i);
    const maybeRoomId = roomIdMatch ? roomIdMatch[1] : null;

    if (maybeRoomId) {
      this.http.get(`/api/room/${maybeRoomId}`).subscribe({
        next: (room: any) => {
          if (!room.is_available) {
            this.messages.push({
              id: this.messageId++,
              text: `❌ Sorry, room "${room.nickname}" is currently unavailable. Please try a different room.`,
              sender: 'bot',
              time: new Date(Date.now())
            });
            this.saveMessagesToLocalStorage();
            this.shouldScroll = true;
            return;
          }

          // Room is available, proceed with chat
          this.fetchChatResponse(trimmed, openaiFormattedHistory, token);
        },
        error: () => {
          // If room check fails, just proceed normally
          this.fetchChatResponse(trimmed, openaiFormattedHistory, token);
        }
      });
    } else {
      // No room mentioned, proceed as usual
      this.fetchChatResponse(trimmed, openaiFormattedHistory, token);
    }
  }

  private fetchChatResponse(
    message: string,
    history: any[],
    token: string | null
  ): void {
    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        history
      })
    })
      .then(async (res) => {
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Error ${res.status}: ${errorText}`);
        }
        return res.json();
      })
      .then((data) => {
        this.messages.push({
          id: this.messageId++,
          text: data.response,
          sender: 'bot',
          time: new Date(Date.now())
        });
        this.saveMessagesToLocalStorage();
        this.shouldScroll = true;
      })
      .catch((err) => {
        this.messages.push({
          id: this.messageId++,
          text: '⚠️ An error occurred. Please try again later or clear your chat history.',
          sender: 'bot',
          time: new Date(Date.now())
        });
        console.error(err);
        this.shouldScroll = true;
      });
  }

  saveMessagesToLocalStorage(): void {
    localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    localStorage.setItem('chatMessageId', this.messageId.toString());
  }

  sendConversationToDatabase(): void {
    const storedRatings = localStorage.getItem('chatRatings');
    const ratings = storedRatings ? JSON.parse(storedRatings) : {};
    const maxRatedMessage = Object.keys(ratings).reduce(
      (max, key) => (ratings[key] > ratings[max] ? key : max),
      Object.keys(ratings)[0] || '0'
    );

    const conversation = {
      created_at: new Date().toISOString(),
      user_id: this.userId,
      chat_history: this.messages.map((m) => m.text),
      rating: ratings[maxRatedMessage] || 0,
      feedback: '',
      outcome: 'Requested Information'
    };

    const token = localStorage.getItem('bearerToken');

    this.http
      .post('/api/conversations', conversation, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .subscribe({
        next: (res) => console.log('Conversation saved:', res),
        error: (err) => console.error('Failed to save conversation:', err)
      });
  }

  loadMessagesFromLocalStorage(): void {
    const storedMessages = localStorage.getItem('chatMessages');
    const storedId = localStorage.getItem('chatMessageId');

    if (storedMessages) {
      const now = new Date();
      const parsed = JSON.parse(storedMessages);

      this.messages = parsed.filter((m: any) => {
        const messageTime = new Date(m.time);
        const diff = now.getTime() - messageTime.getTime();
        return diff < 24 * 60 * 60 * 1000;
      });

      if (this.messages.length === 0) {
        this.messages = [
          {
            id: 1,
            text: "Hi! I'm ChadGPT. How can I help you today?",
            sender: 'bot',
            time: new Date(Date.now())
          }
        ];
        this.messageId = 2;
      }
    }

    if (storedId) {
      this.messageId = parseInt(storedId, 10);
    }
    this.saveMessagesToLocalStorage();
  }

  clearMessages(): void {
    localStorage.removeItem('chatMessages');
    localStorage.removeItem('chatMessageId');
    localStorage.removeItem('chatRatings');
    this.messages = [
      {
        id: 1,
        text: "Hi! I'm ChadGPT. How can I help you today?",
        sender: 'bot',
        time: new Date(Date.now())
      }
    ];
    this.messageId = 2;
    this.ratings = {};
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom(this.justOpenedChat);
      this.shouldScroll = false;
      this.justOpenedChat = false;
    }
  }

  private scrollToBottom(instant = false): void {
    try {
      this.scrollContainer.nativeElement.scrollTo({
        top: this.scrollContainer.nativeElement.scrollHeight,
        behavior: instant ? 'auto' : 'smooth'
      });
    } catch (err) {
      console.error('Scroll error', err);
    }
  }
}
