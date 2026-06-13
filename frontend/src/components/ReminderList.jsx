import { Bell, MessageSquare } from 'lucide-react'

const channelLabel = { sms: '短信', in_app: '站内' }
const eventLabel = { booking_created: '预约成功', booking_canceled: '预约取消' }
const statusLabel = { pending: '待发送', sent: '已发送', failed: '发送失败' }

export function ReminderList({ reminders }) {
  return (
    <section className="panel">
      <div className="section-title">
        <Bell size={18} />
        <h2>提醒记录</h2>
      </div>
      <div className="reminder-list">
        {reminders.length === 0 ? (
          <div className="empty-state">暂无提醒记录</div>
        ) : (
          reminders.map((reminder) => (
            <article className="reminder-item" key={reminder.id}>
              <div className="reminder-icon">
                {reminder.channel === 'sms' ? <MessageSquare size={16} /> : <Bell size={16} />}
              </div>
              <div className="reminder-body">
                <strong>{reminder.contact_name}</strong>
                <span>{reminder.content}</span>
              </div>
              <div className="reminder-meta">
                <span className={`channel-pill ${reminder.channel}`}>{channelLabel[reminder.channel] || reminder.channel}</span>
                <span className={`event-pill ${reminder.event_type}`}>{eventLabel[reminder.event_type] || reminder.event_type}</span>
                <span className={`status-pill ${reminder.status}`}>{statusLabel[reminder.status] || reminder.status}</span>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  )
}
