import { useState } from 'react';
import { Link } from 'react-router-dom';
import { LoginForm } from '@/features/auth/LoginPage';
import { useAuthStore } from '@/store';
import './LandingPage.css';

import aerialImage from './media/kensington-aerial.png';
import contextImage from './media/kensington-context.png';
import streetImage from './media/tree-lined-street.png';
import streetFilm from './media/tree-lined-street.mp4';

const mediaAssets: Record<string, string> = { 'kensington-aerial.png': aerialImage, 'kensington-context.png': contextImage, 'tree-lined-street.png': streetImage, 'tree-lined-street.mp4': streetFilm };
const media = (name: string) => mediaAssets[name];

function StudioEntry({ authenticated }: { authenticated: boolean }) {
  return <aside className="login-card" id="studio" aria-labelledby="login-title">
    <p className="eyebrow">Urban Studies 451</p>
    <h2 id="login-title">{authenticated ? 'Continue your work.' : 'Your project starts here.'}</h2>
    <p className="login-intro">{authenticated ? 'Open your saved projects to continue designing.' : 'Sign in to create a project or continue your saved work.'}</p>
    {authenticated ? <Link className="pill login-submit" to="/projects">Continue to projects</Link> : <LoginForm />}
  </aside>;
}

export function LandingPage() {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isLoading = useAuthStore(state => state.isLoading);
  const [showRender, setShowRender] = useState(false);
  if (isLoading) return <div className="student-landing loading" role="status">Loading City Prompt…</div>;
  return <div className="student-landing"><a className="landing-skip" href="#main-content">Skip to content</a>

    <header className="wrap nav"><a className="brand" href="#main-content" aria-label="City Prompt home"><img src="/images/city-prompt-logo.png" alt="" />CITY PROMPT</a><nav className="navlinks" aria-label="Main navigation"><a href="#how-it-works">Project steps</a><a href="#perspectives">See the context</a><a className="pill" href="#studio">{isAuthenticated ? 'Your projects' : 'Sign in'}</a></nav></header>
    <main id="main-content">
      <section className="hero" aria-labelledby="hero-title"><img src={aerialImage} alt="Kensington Courtyard design study showing the proposal within surrounding streets, transit, buildings and hillside terrain" /><div className="wrap hero-inner"><div className="hero-top"><p className="eyebrow"><span className="dot"></span>Your final-project workspace</p></div><div className="hero-bottom"><div className="hero-story"><p className="course-name">Urban Studies 451 <span>Planning in the Canadian City</span></p><h1 id="hero-title">Build your<br />final project.</h1><p className="hero-copy">City Prompt is a tool to help you understand, build and visualize your final project for Urban Studies 451.</p><div className="hero-actions"><a className="text-link" href="#how-it-works">Start with the steps <span>↓</span></a></div></div><StudioEntry authenticated={isAuthenticated} /></div></div></section>
      <div className="wrap rail"><span className="eyebrow">Site → Design → Present</span><span>Kensington study · Illustrative AI render</span></div>
      <section className="wrap intro" id="how-it-works" aria-labelledby="steps-title">
        <div className="section-top"><div><p className="eyebrow">A guide to getting started</p><h2 id="steps-title">Five steps for<br />your final project.</h2></div><p className="section-note">Use these steps to develop your proposal in City Prompt. Refer to your course assignment for submission requirements and assessment criteria.</p></div>
        <ol className="project-steps">
          <li><span className="step-num">01</span><div><p className="step-stage">Site · Explore</p><h3>Understand the place.</h3><p>Look at the existing buildings, streets and landmarks. Turn on zoning, local area plans and transport layers to understand the wider context. You can explore maps before drawing a boundary.</p></div><p className="step-question">What is here, and what does the area need?</p></li>
          <li><span className="step-num">02</span><div><p className="step-stage">Site · Define</p><h3>Draw your site boundary.</h3><p>Choose the area you will work on. Review existing land uses and the available assessed property values as context for your proposal.</p></div><p className="step-question">Where does your proposal begin and end?</p></li>
          <li><span className="step-num">03</span><div><p className="step-stage">Site · Propose</p><h3>Map your proposed land uses.</h3><p>Draw land-use areas and assign Calgary district codes or a custom designation. Keep your proposal separate from existing zoning and consider the local area plan.</p></div><p className="step-question">What belongs here, and why?</p></li>
          <li><span className="step-num">04</span><div><p className="step-stage">Design · Test</p><h3>Build it. Walk it. Refine it.</h3><p>Add buildings, parks, streets and details. Move and rotate them, then walk through the design. Check connections, public spaces and how your proposal meets its neighbours.</p></div><p className="step-question">How will people use this place?</p></li>
          <li><span className="step-num">05</span><div><p className="step-stage">Present · Explain</p><h3>Show your planning decisions.</h3><p>Review the planning report against your proposed zoning and local area plan. Select maps and views that explain your design, then add your own rationale and check the course submission requirements.</p></div><p className="step-question">What evidence supports your proposal?</p></li>
        </ol></section>
      <section className="wrap perspective" id="perspectives"><div className="section-top"><div><p className="eyebrow">Start with the surrounding city</p><h2>Your site is part<br />of a neighbourhood.</h2></div><div className="tabs" role="group" aria-label="Kensington Courtyard study view"><button className="tab" id="streetTab" type="button" aria-pressed={!showRender} onClick={() => setShowRender(false)}>In the app</button><button className="tab" id="aerialTab" type="button" aria-pressed={showRender} onClick={() => setShowRender(true)}>Example render</button></div></div><figure><div className="pair-image"><img id="pair" src={showRender ? media('kensington-aerial.png') : media('kensington-context.png')} alt={showRender ? 'Illustrative aerial render of Kensington Courtyard' : 'City Prompt showing the proposal within surrounding Google 3D buildings, streets, transit and terrain'} loading="lazy" /></div><figcaption className="caption"><span><strong>Kensington Courtyard</strong><br />Example project · Surrounding streets, transit and terrain</span><span id="pairCaption" aria-live="polite">{showRender ? 'AI render · Illustrative proposal' : 'Actual app view · Google 3D context'}</span></figcaption></figure><div className="context-prompts"><p><strong>Look beyond the boundary.</strong> Identify neighbouring buildings and landmarks that help locate your site.</p><p><strong>Trace the connections.</strong> Consider streets, transit stops, pathways and nearby public spaces.</p><p><strong>Keep the geography visible.</strong> Use the 3D map to check location and scale; use AI renders to communicate your proposal.</p></div></section>
      <section className="film" id="film"><div className="wrap film-grid"><div><p className="eyebrow">Optional · Presentation example</p><h2>Animate a<br />saved render.</h2><p>Once your proposal is ready, a short animation can help illustrate the experience of a place. Use it alongside your maps and planning rationale.</p><small>AI-animated render · 5 seconds · Silent<br />Explore the actual 3D model separately in Walk mode.</small></div><div><div className="film-screen"><video poster={media('tree-lined-street.png')} src={media('tree-lined-street.mp4')} muted playsInline controls preload="none" aria-label="Five-second AI animation of a tree-lined street" /></div><div className="film-caption"><span>Tree-lined street · City Prompt</span><span>Saved render → animated film</span></div></div></div></section>
      <section className="wrap gallery" aria-labelledby="review-title"><div className="section-top"><div><p className="eyebrow">Before you present</p><h2 id="review-title">Check the plan.<br />Explain your choices.</h2></div><p className="section-note">City Prompt helps you explore and communicate a proposal. Your analysis and planning judgement connect the design to the course.</p></div><div className="steps"><article className="step"><h3>Context</h3><p>How does your proposal respond to nearby buildings, landmarks, streets, transit and public spaces?</p></article><article className="step"><h3>Policy & land use</h3><p>Where does your proposal align with the local area plan and your proposed zoning? Explain departures and assumptions.</p></article><article className="step"><h3>Everyday experience</h3><p>Can people move through the site comfortably? Use a walk-through and selected views to check what your plan feels like at ground level.</p></article></div></section>
      <section className="closing"><div className="wrap closing-inner"><div><p className="eyebrow">Ready to work?</p><h2>Open your project.<br />Start with the site.</h2></div><a className="pill" href="#studio">{isAuthenticated ? 'Your projects' : 'Sign in to City Prompt'} <span className="arrow">↗</span></a></div></section>
    </main><footer className="wrap"><a href="#main-content" className="brand"><img src="/images/city-prompt-logo.png" alt="" />CITY PROMPT</a><span>Urban Studies 451 – Planning in the Canadian City</span><a href="#how-it-works">Back to project steps ↑</a></footer><div className="review-note">Illustrative proposals, not approved developments.</div>

  </div>;
}
