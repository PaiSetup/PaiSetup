From f699934b8c8a9c15988ad359bf8fedd6c55abd53 Mon Sep 17 00:00:00 2001
From: Thomas Oltmann <thomas.oltmann.hhg@gmail.com>
Date: Wed, 13 Jun 2018 19:46:26 +0200
Subject: [PATCH] Allow dwm to have translucent bars, while keeping all the
 text on it opaque, just like the alpha-patch for st. Updated for b69c870.

---
 config.def.h |  7 ++++++
 config.mk    |  2 +-
 drw.c        | 26 ++++++++++++-----------
 drw.h        |  9 +++++---
 dwm.c        | 60 ++++++++++++++++++++++++++++++++++++++++++++++------
 5 files changed, 82 insertions(+), 22 deletions(-)

diff --git a/config.def.h b/config.def.h
index 1c0b587..4f68fe8 100644
--- a/config.def.h
+++ b/config.def.h
@@ -12,11 +12,18 @@ static const char col_gray2[]       = "#444444";
 static const char col_gray4[]       = "#eeeeee";
 static const char col_cyan[]        = "#005577";
 static const char col_urgborder[]   = "#ff0000";
+static const unsigned int baralpha = 0xd0;
+static const unsigned int borderalpha = OPAQUE;
 static const char *colors[][3]      = {
 	/*               fg         bg         border   */
 	[SchemeNorm] = { col_gray3, col_gray1, col_gray2 },
 	[SchemeSel]  = { col_gray4, col_cyan,  col_cyan  },
	[SchemeUrg]  = { col_gray4, col_cyan,  col_urgborder  },
 };
+static const unsigned int alphas[][3]      = {
+	/*               fg      bg        border     */
+	[SchemeNorm] = { OPAQUE, baralpha, borderalpha },
+	[SchemeSel]  = { OPAQUE, baralpha, borderalpha },
+};
 
 /* tagging */
 static const char *tags[] = { "1", "2", "3", "4", "5", "6", "7", "8", "9" };
diff --git a/config.mk b/config.mk
index 25e2685..bef8de0 100644
--- a/config.mk
+++ b/config.mk
@@ -22,7 +22,7 @@ FREETYPEINC = /usr/include/freetype2
 
 # includes and libs
 INCS = -I${X11INC} -I${FREETYPEINC}
-LIBS = -L${X11LIB} -lX11 ${XINERAMALIBS} ${FREETYPELIBS}
+LIBS = -L${X11LIB} -lX11 ${XINERAMALIBS} ${FREETYPELIBS} -lXrender
 
 # flags
 CPPFLAGS = -D_DEFAULT_SOURCE -D_BSD_SOURCE -D_POSIX_C_SOURCE=2 -DVERSION=\"${VERSION}\" ${XINERAMAFLAGS}
diff --git a/drw.c b/drw.c
index c638323..77fc113 100644
--- a/drw.c
+++ b/drw.c
@@ -61,7 +61,7 @@ utf8decode(const char *c, long *u, size_t clen)
 }
 
 Drw *
-drw_create(Display *dpy, int screen, Window root, unsigned int w, unsigned int h)
+drw_create(Display *dpy, int screen, Window root, unsigned int w, unsigned int h, Visual *visual, unsigned int depth, Colormap cmap)
 {
 	Drw *drw = ecalloc(1, sizeof(Drw));
 
@@ -70,8 +70,11 @@ drw_create(Display *dpy, int screen, Window root, unsigned int w, unsigned int h
 	drw->root = root;
 	drw->w = w;
 	drw->h = h;
-	drw->drawable = XCreatePixmap(dpy, root, w, h, DefaultDepth(dpy, screen));
-	drw->gc = XCreateGC(dpy, root, 0, NULL);
+	drw->visual = visual;
+	drw->depth = depth;
+	drw->cmap = cmap;
+	drw->drawable = XCreatePixmap(dpy, root, w, h, depth);
+	drw->gc = XCreateGC(dpy, drw->drawable, 0, NULL);
 	XSetLineAttributes(dpy, drw->gc, 1, LineSolid, CapButt, JoinMiter);
 
 	return drw;
@@ -87,7 +90,7 @@ drw_resize(Drw *drw, unsigned int w, unsigned int h)
 	drw->h = h;
 	if (drw->drawable)
 		XFreePixmap(drw->dpy, drw->drawable);
-	drw->drawable = XCreatePixmap(drw->dpy, drw->root, w, h, DefaultDepth(drw->dpy, drw->screen));
+	drw->drawable = XCreatePixmap(drw->dpy, drw->root, w, h, drw->depth);
 }
 
 void
@@ -180,21 +183,22 @@ drw_fontset_free(Fnt *font)
 }
 
 void
-drw_clr_create(Drw *drw, Clr *dest, const char *clrname)
+drw_clr_create(Drw *drw, Clr *dest, const char *clrname, unsigned int alpha)
 {
 	if (!drw || !dest || !clrname)
 		return;
 
-	if (!XftColorAllocName(drw->dpy, DefaultVisual(drw->dpy, drw->screen),
-	                       DefaultColormap(drw->dpy, drw->screen),
+	if (!XftColorAllocName(drw->dpy, drw->visual, drw->cmap,
 	                       clrname, dest))
 		die("error, cannot allocate color '%s'", clrname);
+
+	dest->pixel = (dest->pixel & 0x00ffffffU) | (alpha << 24);
 }
 
 /* Wrapper to create color schemes. The caller has to call free(3) on the
  * returned color scheme when done using it. */
 Clr *
-drw_scm_create(Drw *drw, const char *clrnames[], size_t clrcount)
+drw_scm_create(Drw *drw, const char *clrnames[], const unsigned int alphas[], size_t clrcount)
 {
 	size_t i;
 	Clr *ret;
@@ -204,7 +208,7 @@ drw_scm_create(Drw *drw, const char *clrnames[], size_t clrcount)
 		return NULL;
 
 	for (i = 0; i < clrcount; i++)
-		drw_clr_create(drw, &ret[i], clrnames[i]);
+		drw_clr_create(drw, &ret[i], clrnames[i], alphas[i]);
 	return ret;
 }
 
@@ -260,9 +264,7 @@ drw_text(Drw *drw, int x, int y, unsigned int w, unsigned int h, unsigned int lp
 	} else {
 		XSetForeground(drw->dpy, drw->gc, drw->scheme[invert ? ColFg : ColBg].pixel);
 		XFillRectangle(drw->dpy, drw->drawable, drw->gc, x, y, w, h);
-		d = XftDrawCreate(drw->dpy, drw->drawable,
-		                  DefaultVisual(drw->dpy, drw->screen),
-		                  DefaultColormap(drw->dpy, drw->screen));
+		d = XftDrawCreate(drw->dpy, drw->drawable, drw->visual, drw->cmap);
 		x += lpad;
 		w -= lpad;
 	}
diff --git a/drw.h b/drw.h
index 4bcd5ad..a56f523 100644
--- a/drw.h
+++ b/drw.h
@@ -20,6 +20,9 @@ typedef struct {
 	Display *dpy;
 	int screen;
 	Window root;
+	Visual *visual;
+	unsigned int depth;
+	Colormap cmap;
 	Drawable drawable;
 	GC gc;
 	Clr *scheme;
@@ -27,7 +30,7 @@ typedef struct {
 } Drw;
 
 /* Drawable abstraction */
-Drw *drw_create(Display *dpy, int screen, Window win, unsigned int w, unsigned int h);
+Drw *drw_create(Display *dpy, int screen, Window win, unsigned int w, unsigned int h, Visual *visual, unsigned int depth, Colormap cmap);
 void drw_resize(Drw *drw, unsigned int w, unsigned int h);
 void drw_free(Drw *drw);
 
@@ -38,8 +41,8 @@ unsigned int drw_fontset_getwidth(Drw *drw, const char *text);
 void drw_font_getexts(Fnt *font, const char *text, unsigned int len, unsigned int *w, unsigned int *h);
 
 /* Colorscheme abstraction */
-void drw_clr_create(Drw *drw, Clr *dest, const char *clrname);
-Clr *drw_scm_create(Drw *drw, const char *clrnames[], size_t clrcount);
+void drw_clr_create(Drw *drw, Clr *dest, const char *clrname, unsigned int alpha);
+Clr *drw_scm_create(Drw *drw, const char *clrnames[], const unsigned int alphas[], size_t clrcount);
 
 /* Cursor abstraction */
 Cur *drw_cur_create(Drw *drw, int shape);
diff --git a/dwm.c b/dwm.c
index 4465af1..20f8309 100644
--- a/dwm.c
+++ b/dwm.c
@@ -57,6 +57,8 @@
 #define TAGMASK                 ((1 << LENGTH(tags)) - 1)
 #define TEXTW(X)                (drw_fontset_getwidth(drw, (X)) + lrpad)
 
+#define OPAQUE                  0xffU
+
 /* enums */
 enum { CurNormal, CurResize, CurMove, CurLast }; /* cursor */
 enum { SchemeNorm, SchemeSel }; /* color schemes */
@@ -232,6 +234,7 @@ static Monitor *wintomon(Window w);
 static int xerror(Display *dpy, XErrorEvent *ee);
 static int xerrordummy(Display *dpy, XErrorEvent *ee);
 static int xerrorstart(Display *dpy, XErrorEvent *ee);
+static void xinitvisual();
 static void zoom(const Arg *arg);
 
 /* variables */
@@ -268,6 +271,11 @@ static Drw *drw;
 static Monitor *mons, *selmon;
 static Window root, wmcheckwin;
 
+static int useargb = 0;
+static Visual *visual;
+static int depth;
+static Colormap cmap;
+
 /* configuration, allows nested code to access above variables */
 #include "config.h"
 
@@ -1541,7 +1549,8 @@ setup(void)
 	sw = DisplayWidth(dpy, screen);
 	sh = DisplayHeight(dpy, screen);
 	root = RootWindow(dpy, screen);
-	drw = drw_create(dpy, screen, root, sw, sh);
+	xinitvisual();
+	drw = drw_create(dpy, screen, root, sw, sh, visual, depth, cmap);
 	if (!drw_fontset_create(drw, fonts, LENGTH(fonts)))
 		die("no fonts could be loaded.");
 	lrpad = drw->fonts->h;
@@ -1569,7 +1578,7 @@ setup(void)
 	/* init appearance */
 	scheme = ecalloc(LENGTH(colors), sizeof(Clr *));
 	for (i = 0; i < LENGTH(colors); i++)
-		scheme[i] = drw_scm_create(drw, colors[i], 3);
+		scheme[i] = drw_scm_create(drw, colors[i], alphas[i], 3);
 	/* init bars */
 	updatebars();
 	updatestatus();
@@ -1804,16 +1813,18 @@ updatebars(void)
 	Monitor *m;
 	XSetWindowAttributes wa = {
 		.override_redirect = True,
-		.background_pixmap = ParentRelative,
+		.background_pixel = 0,
+		.border_pixel = 0,
+		.colormap = cmap,
 		.event_mask = ButtonPressMask|ExposureMask
 	};
 	XClassHint ch = {"dwm", "dwm"};
 	for (m = mons; m; m = m->next) {
 		if (m->barwin)
 			continue;
-		m->barwin = XCreateWindow(dpy, root, m->wx, m->by, m->ww, bh, 0, DefaultDepth(dpy, screen),
-				CopyFromParent, DefaultVisual(dpy, screen),
-				CWOverrideRedirect|CWBackPixmap|CWEventMask, &wa);
+		m->barwin = XCreateWindow(dpy, root, m->wx, m->by, m->ww, bh, 0, depth,
+		                          InputOutput, visual,
+		                          CWOverrideRedirect|CWBackPixel|CWBorderPixel|CWColormap|CWEventMask, &wa);
 		XDefineCursor(dpy, m->barwin, cursor[CurNormal]->cursor);
 		XMapRaised(dpy, m->barwin);
 		XSetClassHint(dpy, m->barwin, &ch);
@@ -2110,6 +2121,43 @@ xerrorstart(Display *dpy, XErrorEvent *ee)
 	return -1;
 }
 
+void
+xinitvisual()
+{
+	XVisualInfo *infos;
+	XRenderPictFormat *fmt;
+	int nitems;
+	int i;
+
+	XVisualInfo tpl = {
+		.screen = screen,
+		.depth = 32,
+		.class = TrueColor
+	};
+	long masks = VisualScreenMask | VisualDepthMask | VisualClassMask;
+
+	infos = XGetVisualInfo(dpy, masks, &tpl, &nitems);
+	visual = NULL;
+	for(i = 0; i < nitems; i ++) {
+		fmt = XRenderFindVisualFormat(dpy, infos[i].visual);
+		if (fmt->type == PictTypeDirect && fmt->direct.alphaMask) {
+			visual = infos[i].visual;
+			depth = infos[i].depth;
+			cmap = XCreateColormap(dpy, root, visual, AllocNone);
+			useargb = 1;
+			break;
+		}
+	}
+
+	XFree(infos);
+
+	if (! visual) {
+		visual = DefaultVisual(dpy, screen);
+		depth = DefaultDepth(dpy, screen);
+		cmap = DefaultColormap(dpy, screen);
+	}
+}
+
 void
 zoom(const Arg *arg)
 {
-- 
2.17.0

