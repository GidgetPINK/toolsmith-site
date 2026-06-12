import { Resend } from 'resend'
import { createClient } from '@supabase/supabase-js'

const resend = new Resend(process.env.RESEND_API_KEY)
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

const ALLOWED_ORIGINS = [
  'https://thetoolsmithapp.com',
  'https://www.thetoolsmithapp.com'
]

function isValidEmail(email) {
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(email)
}

export default async function handler(req, res) {
  const origin = req.headers.origin
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin)
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { name, email, biggest_headache, user_agent } = req.body || {}

    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({ error: 'Name is required' })
    }
    if (name.length > 100) {
      return res.status(400).json({ error: 'Name is too long' })
    }
    if (!email || typeof email !== 'string' || !isValidEmail(email.trim())) {
      return res.status(400).json({ error: 'Please enter a valid email address' })
    }
    if (biggest_headache && typeof biggest_headache === 'string' && biggest_headache.length > 1000) {
      return res.status(400).json({ error: 'Headache field is too long' })
    }

    const cleanName = name.trim()
    const cleanEmail = email.trim().toLowerCase()
    const cleanHeadache = (biggest_headache && typeof biggest_headache === 'string')
      ? biggest_headache.trim() || null
      : null

    const { error: dbError } = await supabase
      .from('waitlist_signups')
      .insert({
        name: cleanName,
        email: cleanEmail,
        biggest_headache: cleanHeadache,
        source: 'prelaunch-landing',
        user_agent: user_agent || null
      })

    if (dbError) {
      if (dbError.code === '23505' || (dbError.message && dbError.message.includes('duplicate'))) {
        return res.status(409).json({ error: 'That email is already on the waitlist. Thanks for your enthusiasm!' })
      }
      if (dbError.message && dbError.message.includes('email_format')) {
        return res.status(400).json({ error: 'Please enter a valid email address' })
      }
      console.error('Database error:', dbError)
      return res.status(500).json({ error: 'Something went wrong. Please try again.' })
    }

    try {
      await resend.emails.send({
        from: 'The Toolsmith <hello@thetoolsmithapp.com>',
        to: cleanEmail,
        subject: 'You\'re on the Toolsmith waitlist',
        html: buildEmailHtml(cleanName),
        text: buildEmailText(cleanName)
      })
    } catch (emailError) {
      console.error('Email send failed (signup succeeded):', emailError)
    }

    return res.status(200).json({ success: true })
  } catch (err) {
    console.error('Unexpected error:', err)
    return res.status(500).json({ error: 'Something went wrong. Please try again.' })
  }
}

function buildEmailText(name) {
  return `Hey ${name},

Thanks for joining The Toolsmith waitlist.

We're putting the finishing touches on the app and you're now on the list to hear about it first. No spam, no sales pitches. Just one note when we open the doors.

If you have a minute, hit reply and tell us what's broken in your current maintenance workflow. Real feedback shapes what we build.

Talk soon,
The Toolsmith team

The Toolsmith LLC. Built in Alabama.
`
}

function buildEmailHtml(name) {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>You're on the Toolsmith waitlist</title>
</head>
<body style="margin:0;padding:0;background:#1a1a2e;font-family:Georgia,serif;color:#f8f6f1;">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#1a1a2e;">
    <tr>
      <td align="center" style="padding:40px 20px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="560" style="max-width:560px;background:#16213e;border:1px solid rgba(201,168,76,0.18);border-radius:14px;">
          <tr>
            <td style="padding:40px 36px;">
              <p style="margin:0 0 8px 0;color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-family:'Helvetica Neue',Arial,sans-serif;">You're on the list</p>
              <h1 style="margin:0 0 24px 0;font-family:Georgia,serif;color:#f8f6f1;font-size:28px;font-weight:500;line-height:1.25;">Welcome to The Toolsmith</h1>
              
              <p style="margin:0 0 20px 0;color:#c5c8d9;font-size:16px;line-height:1.65;font-family:Georgia,serif;">
                Hey ${name},
              </p>
              
              <p style="margin:0 0 20px 0;color:#c5c8d9;font-size:16px;line-height:1.65;font-family:Georgia,serif;">
                Thanks for joining the waitlist. We're putting the finishing touches on the app and you're now on the list to hear about it first. No spam, no sales pitches. Just one note when we open the doors.
              </p>
              
              <p style="margin:0 0 20px 0;color:#c5c8d9;font-size:16px;line-height:1.65;font-family:Georgia,serif;">
                If you have a minute, hit reply and tell us what's broken in your current maintenance workflow. Real feedback shapes what we build.
              </p>
              
              <p style="margin:32px 0 0 0;color:#c5c8d9;font-size:16px;line-height:1.65;font-family:Georgia,serif;">
                Talk soon,<br>
                <span style="color:#c9a84c;">The Toolsmith team</span>
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 36px;border-top:1px solid rgba(201,168,76,0.18);">
              <p style="margin:0;color:#8e92a8;font-size:12px;line-height:1.5;font-family:'Helvetica Neue',Arial,sans-serif;text-align:center;">
                The Toolsmith LLC. Built in Alabama.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`
}