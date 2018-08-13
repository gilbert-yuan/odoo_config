dnl $Id: config.m4 324533 2012-03-25 20:01:35Z tony2001 $

PHP_ARG_WITH(sphinx, for sphinx support,
[  --with-sphinx             Include sphinx support])

if test "$PHP_SPHINX" != "no"; then

  SEARCH_PATH="/usr/local /usr /local /opt"
  SEARCH_FOR="/include/sphinxclient.h"

  if test "$PHP_SPHINX" = "yes"; then
    AC_MSG_CHECKING([for libsphinxclient headers in default path])
    for i in $SEARCH_PATH ; do
      if test -r $i/$SEARCH_FOR; then
        SPHINX_DIR=$i
        AC_MSG_RESULT(found in $i)
      fi
    done
  else 
    AC_MSG_CHECKING([for libsphinxclient headers in $PHP_SPHINX])
    if test -r $PHP_SPHINX/$SEARCH_FOR; then
      SPHINX_DIR=$PHP_SPHINX
      AC_MSG_RESULT([found])
    fi
  fi

  if test -z "$SPHINX_DIR"; then
    AC_MSG_RESULT([not found])
    AC_MSG_ERROR([Cannot find libsphinxclient headers])
  fi

  PHP_ADD_INCLUDE($SPHINX_DIR/include)

  LIBNAME=sphinxclient
  LIBSYMBOL=sphinx_create

  PHP_CHECK_LIBRARY($LIBNAME,$LIBSYMBOL,
  [
    PHP_ADD_LIBRARY_WITH_PATH($LIBNAME, $SPHINX_DIR/$PHP_LIBDIR, SPHINX_SHARED_LIBADD)
    AC_DEFINE(HAVE_SPHINXLIB,1,[ ])
  ],[
    AC_MSG_ERROR([wrong libsphinxclient version or lib not found])
  ],[
    -L$SPHINX_DIR/$PHP_LIBDIR -lm
  ])
  
  PHP_CHECK_LIBRARY($LIBNAME,sphinx_get_string,
  [
    PHP_ADD_LIBRARY_WITH_PATH($LIBNAME, $SPHINX_DIR/$PHP_LIBDIR, SPHINX_SHARED_LIBADD)
    AC_DEFINE(LIBSPHINX_VERSION_ID,110,[ ])
    LIBSPHINX_VERSION_ID="110"
  ],[],[
    -L$SPHINX_DIR/$PHP_LIBDIR -lm
  ])

  if test "x$LIBSPHINX_VERSION_ID" = "x"; then
    PHP_CHECK_LIBRARY($LIBNAME,sphinx_set_select,
    [
      PHP_ADD_LIBRARY_WITH_PATH($LIBNAME, $SPHINX_DIR/$PHP_LIBDIR, SPHINX_SHARED_LIBADD)
      AC_DEFINE(LIBSPHINX_VERSION_ID,99,[ ])
      LIBSPHINX_VERSION_ID="99"
    ],[],[
      -L$SPHINX_DIR/$PHP_LIBDIR -lm
    ])
  fi

  if test "x$LIBSPHINX_VERSION_ID" = "x"; then
    AC_DEFINE(LIBSPHINX_VERSION_ID,98,[ ])
  fi

  _SAVE_CFLAGS=$CFLAGS
  CFLAGS="$CFLAGS -I$SPHINX_DIR/include"
  AC_CACHE_CHECK([for new sphinx_set_ranking_mode() signature], ac_cv_3arg_setrankingmode,
    [AC_TRY_COMPILE([#include <sphinxclient.h>], [sphinx_set_ranking_mode(0, 0, 0)],
    ac_cv_3arg_setrankingmode=yes, ac_cv_3arg_setrankingmode=no)])
  if test "$ac_cv_3arg_setrankingmode" = yes; then
    AC_DEFINE(HAVE_3ARG_SPHINX_SET_RANKING_MODE,1,[Whether we have 3 arg sphinx_set_ranking_mode()])
  fi
  CFLAGS=$_SAVE_CFLAGS

  PHP_SUBST(SPHINX_SHARED_LIBADD)

  PHP_NEW_EXTENSION(sphinx, sphinx.c, $ext_shared)
fi
